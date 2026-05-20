import os
import docker
from kubernetes import client, config
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from generator import generate_docker_config

# Try to load K8s config
try:
    config.load_kube_config()
except Exception as e:
    print(f"Warning: Could not load kubernetes config: {e}")

# Try to load Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Warning: Could not load docker client: {e}")
    docker_client = None

class K8sStatusInput(BaseModel):
    namespace: str = Field(default="default", description="The Kubernetes namespace to check")

@tool("get_k8s_status", args_schema=K8sStatusInput)
def get_k8s_status(namespace: str = "default") -> str:
    """Fetches pod status and events from the specified Kubernetes namespace."""
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        
        result = []
        for pod in pods.items:
            status = pod.status.phase
            # Check for specific container statuses like CrashLoopBackOff
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    if container_status.state.waiting and container_status.state.waiting.reason:
                        status = container_status.state.waiting.reason
                        
            result.append(f"Pod: {pod.metadata.name}, Status: {status}")
            
        if not result:
            return f"No pods found in namespace '{namespace}'."
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching k8s status: {e}"

class PodLogsInput(BaseModel):
    pod_name: str = Field(..., description="The name of the pod to fetch logs from")
    namespace: str = Field(default="default", description="The Kubernetes namespace of the pod")

@tool("get_pod_logs", args_schema=PodLogsInput)
def get_pod_logs(pod_name: str, namespace: str = "default") -> str:
    """Fetches the logs for a specific Kubernetes pod."""
    try:
        v1 = client.CoreV1Api()
        # Get the last 100 lines of logs to avoid overwhelming the LLM
        logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=100)
        return logs
    except Exception as e:
        return f"Error fetching logs for pod {pod_name}: {e}"

class DockerStatsInput(BaseModel):
    pass

@tool("get_docker_stats", args_schema=DockerStatsInput)
def get_docker_stats() -> str:
    """Lists local Docker containers and their current status/stats."""
    if not docker_client:
        return "Docker client is not initialized."
    
    try:
        containers = docker_client.containers.list(all=True)
        result = []
        for container in containers:
            status = container.status
            name = container.name
            image = container.image.tags[0] if container.image.tags else "unknown"
            
            # Optionally get more stats if running
            stats_str = ""
            if status == "running":
                # stats(stream=False) can be slow, so we just get basic info
                stats = container.stats(stream=False)
                # Calculate memory usage
                mem_usage = stats.get('memory_stats', {}).get('usage', 0)
                mem_limit = stats.get('memory_stats', {}).get('limit', 0)
                if mem_limit > 0:
                    mem_percent = (mem_usage / mem_limit) * 100
                    stats_str = f" - Mem: {mem_percent:.2f}%"
                    
            result.append(f"Container: {name} (Image: {image}), Status: {status}{stats_str}")
            
        if not result:
            return "No Docker containers found."
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching docker stats: {e}"

class CreateDockerInput(BaseModel):
    image: str = Field(..., description="The Docker image to run (e.g., 'nginx:latest')")
    name: str = Field(default=None, description="Optional name for the container")
    detach: bool = Field(default=True, description="Run container in background")
    ports: dict = Field(default=None, description="Port mapping, e.g., {'80/tcp': 8080}")

class GenerateDockerfileInput(BaseModel):
    path: str = Field(..., description="Path to the directory where the Dockerfile should be created.")
    description: str = Field(..., description="Description of the project (tech stack, ports, etc.) to generate the correct Dockerfile.")

@tool("generate_dockerfile_for_project", args_schema=GenerateDockerfileInput)
def generate_dockerfile_for_project(path: str, description: str) -> str:
    """Generates a Dockerfile using AI and saves it to the specified project path."""
    try:
        if not os.path.exists(path):
            return f"Error: The path '{path}' does not exist on the host system. Please verify the path."
            
        dockerfile_path = os.path.join(path, "Dockerfile")
        if os.path.exists(dockerfile_path):
            return f"Warning: A Dockerfile already exists at '{dockerfile_path}'. If you want to rebuild, just use build_docker_image."
            
        # Call the generator logic
        config = generate_docker_config(description)
        dockerfile_content = config.get("dockerfile", "")
        
        if not dockerfile_content:
            return "Error: Failed to generate Dockerfile content."
            
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
            
        return f"Successfully generated and saved Dockerfile at '{dockerfile_path}'. You can now build the image."
    except Exception as e:
        return f"Error generating Dockerfile: {e}"

class BuildDockerInput(BaseModel):
    path: str = Field(..., description="Path to the directory containing the Dockerfile (build context).")
    tag: str = Field(..., description="Name and optionally a tag in the 'name:tag' format to apply to the new image.")

@tool("build_docker_image", args_schema=BuildDockerInput)
def build_docker_image(path: str, tag: str) -> str:
    """Builds a new Docker image from a specified directory path (build context)."""
    if not docker_client:
        return "Docker client is not initialized."
    try:
        if not os.path.exists(path):
            return f"Error: The path '{path}' does not exist on the host system."
            
        image, logs = docker_client.images.build(
            path=path,
            tag=tag,
            rm=True
        )
        return f"Successfully built image '{tag}' (ID: {image.short_id})."
    except docker.errors.BuildError as e:
        return f"Build failed: {e.msg}"
    except docker.errors.APIError as e:
        return f"API error during build: {e.explanation}"
    except Exception as e:
        return f"Error building docker image: {e}"

@tool("create_docker_container", args_schema=CreateDockerInput)
def create_docker_container(image: str, name: str = None, detach: bool = True, ports: dict = None) -> str:
    """Creates and starts a new Docker container."""
    if not docker_client:
        return "Docker client is not initialized."
    try:
        # Pull the image first if not available locally
        try:
            docker_client.images.get(image)
        except docker.errors.ImageNotFound:
            docker_client.images.pull(image)
            
        container = docker_client.containers.run(
            image=image,
            name=name,
            detach=detach,
            ports=ports
        )
        return f"Successfully started container {container.name} (ID: {container.short_id}) from image {image}."
    except Exception as e:
        return f"Error creating docker container: {e}"
