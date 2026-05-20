import docker
import tempfile
import os

try:
    client = docker.from_env()
    
    dockerfile_content = """
    FROM alpine:latest
    CMD ["echo", "Hello from auto-built container!"]
    """
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
            
        print("Building image...")
        image, logs = client.images.build(path=temp_dir, tag="auto-test-image:latest")
        print("Image built successfully.")
        
        print("Running container...")
        container = client.containers.run("auto-test-image:latest", detach=True)
        print(f"Container {container.name} started.")
        print(container.logs().decode("utf-8"))
        
except Exception as e:
    print(f"Error: {e}")
