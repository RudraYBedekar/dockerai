const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const projectList = document.getElementById('project-list');
const newProjectBtn = document.getElementById('new-project-btn');
const projectModal = document.getElementById('project-modal');
const saveProjBtn = document.getElementById('save-proj-btn');
const cancelProjBtn = document.getElementById('cancel-proj-btn');
const currentProjectTitle = document.getElementById('current-project-title');
const currentProjectContext = document.getElementById('current-project-context');

let currentProjectId = null;
let projects = [];

// Initialize
async function init() {
    await loadProjects();
}

async function loadProjects() {
    const res = await fetch('/api/projects');
    projects = await res.json();
    renderProjects();
    
    if (projects.length > 0 && !currentProjectId) {
        selectProject(projects[0].id);
    }
}

function renderProjects() {
    projectList.innerHTML = '';
    projects.forEach(p => {
        const li = document.createElement('li');
        li.className = p.id === currentProjectId ? 'active' : '';
        li.innerHTML = `
            <h4>${p.name}</h4>
            <p>${p.context}</p>
        `;
        li.onclick = () => selectProject(p.id);
        projectList.appendChild(li);
    });
}

async function selectProject(id) {
    currentProjectId = id;
    const proj = projects.find(p => p.id === id);
    if (!proj) return;
    
    currentProjectTitle.textContent = proj.name;
    currentProjectContext.textContent = `Context: ${proj.context}`;
    
    // Enable inputs
    userInput.disabled = false;
    sendBtn.disabled = false;
    
    renderProjects(); // update active class
    
    // Load history
    chatBox.innerHTML = '';
    const res = await fetch(`/api/projects/${id}/chat`);
    const messages = await res.json();
    
    if (messages.length === 0) {
        appendSystemMessage("Project loaded. Send a message to start chatting!");
    } else {
        messages.forEach(m => {
            const tools = m.tools_used ? JSON.parse(m.tools_used) : [];
            appendMessage(m.role, m.content, tools);
        });
    }
}

// Modal handling
newProjectBtn.onclick = () => {
    projectModal.classList.remove('hidden');
    document.getElementById('proj-name').value = '';
    document.getElementById('proj-context').value = '';
};

cancelProjBtn.onclick = () => {
    projectModal.classList.add('hidden');
};

saveProjBtn.onclick = async () => {
    const name = document.getElementById('proj-name').value.trim();
    const context = document.getElementById('proj-context').value.trim();
    if (!name || !context) return alert('Name and Context are required');
    
    saveProjBtn.disabled = true;
    const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, context })
    });
    const newProj = await res.json();
    saveProjBtn.disabled = false;
    projectModal.classList.add('hidden');
    
    await loadProjects();
    selectProject(newProj.id);
};

// Chat handling
function appendSystemMessage(content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ai-message`;
    msgDiv.innerHTML = `<div class="message-content" style="opacity: 0.8; font-style: italic;">${content}</div>`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(role, content, tools = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    
    let innerHTML = '';
    if (role === 'ai') {
        innerHTML += `<div class="message-content">${marked.parse(content)}</div>`;
        if (tools && tools.length > 0) {
            innerHTML += `<div class="tools-used">`;
            innerHTML += `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
            const uniqueTools = [...new Set(tools)];
            uniqueTools.forEach(t => {
                innerHTML += `<span class="tool-badge">${t}</span>`;
            });
            innerHTML += `</div>`;
        }
    } else {
        innerHTML += `<div class="message-content">${content}</div>`;
    }
    
    msgDiv.innerHTML = innerHTML;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const loader = document.createElement('div');
    loader.className = 'message ai-message loading-indicator';
    loader.innerHTML = `
        <div class="message-content">
            <div class="loading"><span></span><span></span><span></span></div>
        </div>
    `;
    chatBox.appendChild(loader);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loader;
}

async function sendMessage() {
    if (!currentProjectId) return;
    
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    const loader = showLoading();

    try {
        const response = await fetch(`/api/projects/${currentProjectId}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        loader.remove();

        if (data.error) {
            appendMessage('ai', `**Error:** ${data.error}`);
        } else {
            appendMessage('ai', data.response, data.tools_used);
        }
    } catch (err) {
        loader.remove();
        appendMessage('ai', `**Error:** Could not connect to the server.`);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Start
init();
