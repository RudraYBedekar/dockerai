document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const descriptionInput = document.getElementById('project-description');
    const errorMsg = document.getElementById('error-message');
    const spinner = generateBtn.querySelector('.spinner');
    const btnText = generateBtn.querySelector('span');
    
    const loadingOverlay = document.getElementById('loading-overlay');
    const placeholderState = document.getElementById('placeholder-state');
    const resultsPanel = document.getElementById('results');
    
    // UI Elements for Data
    const resType = document.getElementById('res-type');
    const resImage = document.getElementById('res-image');
    const resDockerfile = document.getElementById('res-dockerfile');
    const resRunconfig = document.getElementById('res-runconfig');
    
    // Copy buttons
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetId = e.target.getAttribute('data-target');
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
                navigator.clipboard.writeText(targetEl.textContent).then(() => {
                    const originalText = e.target.textContent;
                    e.target.textContent = 'Copied!';
                    setTimeout(() => {
                        e.target.textContent = originalText;
                    }, 2000);
                });
            }
        });
    });

    generateBtn.addEventListener('click', async () => {
        const description = descriptionInput.value.trim();
        if (!description) {
            showError("Please enter a project description.");
            return;
        }

        // Reset UI State
        hideError();
        setLoading(true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ description })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to generate configuration.");
            }

            // Populate Results
            resType.textContent = data.project_type || "Unknown";
            resImage.textContent = data.base_image || "Unknown";
            resDockerfile.textContent = data.dockerfile || "";
            resRunconfig.textContent = JSON.stringify(data.run_config, null, 2);

            // Trigger PrismJS syntax highlighting
            if (window.Prism) {
                Prism.highlightElement(resDockerfile);
                Prism.highlightElement(resRunconfig);
            }

            showResults();

        } catch (error) {
            showError(error.message);
            resetPanels();
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.textContent = "Generating...";
            spinner.classList.remove('hidden');
            
            placeholderState.classList.add('hidden');
            resultsPanel.classList.add('hidden');
            loadingOverlay.classList.remove('hidden');
        } else {
            generateBtn.disabled = false;
            btnText.textContent = "Generate Config";
            spinner.classList.add('hidden');
            loadingOverlay.classList.add('hidden');
        }
    }

    function showResults() {
        placeholderState.classList.add('hidden');
        loadingOverlay.classList.add('hidden');
        resultsPanel.classList.remove('hidden');
    }

    function resetPanels() {
        placeholderState.classList.remove('hidden');
        loadingOverlay.classList.add('hidden');
        resultsPanel.classList.add('hidden');
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }

    function hideError() {
        errorMsg.classList.add('hidden');
    }
});
