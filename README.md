# DevOps AI Agent (Agentic K8s Docker Tool)

This project is a Python-based intelligent agent built with LangGraph, LangChain, and FastAPI. It serves as an AI DevOps assistant that can perform natural language analysis of your containerized infrastructure, orchestrating interactions with the official Docker and Kubernetes SDKs.

## Features

* **Natural Language Queries:** Ask questions about your infrastructure in plain English.
* **Kubernetes Integration:** 
  * Fetches pod statuses and events from any namespace.
  * Automatically retrieves pod logs when it detects unhealthy pods (e.g., `CrashLoopBackOff`, `Error`).
* **Docker Integration:**
  * Lists local Docker containers and monitors their current memory usage and stats.
  * Can autonomously create and run new Docker containers upon user request.
* **Dual Interfaces:**
  * Interactive Command Line Interface (CLI).
  * Web-based UI served via FastAPI.

## Prerequisites

* Python 3.8+
* Docker running locally (Docker Desktop or Engine).
* Kubernetes cluster access (e.g., Minikube, Docker Desktop K8s) with `~/.kube/config` properly configured.
* An OpenAI API Key for the LangChain agent.

## Setup Instructions

1. **Install dependencies:**
   Ensure you are in the `dockerai` directory and install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables:**
   Copy the example `.env` file or create a new one:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to include your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### 1. Command Line Interface (CLI)
To run the agent directly in your terminal:
```bash
python main.py
```
Type your queries at the prompt, and type `exit` to quit.

### 2. Web UI (FastAPI)
To launch the FastAPI server and access the web interface:
```bash
python app.py
```
Open your browser and navigate to: `http://localhost:8000/ui`

---

## Docker Configuration (Web App Containerization)

*Note: The following Docker commands are configured specifically for building and serving a production web frontend (e.g., React/Vite).*

This project includes a fully containerized setup using a multi-stage `Dockerfile` and `docker-compose.yml`.

### How to build the image

To build the Docker image manually, run the following command in the terminal:
```bash
docker build -t dockmate-ai .
```

### How to run the container

Once the image is built, you can run the container using:
```bash
docker run -p 3000:80 --name dockmate-ai-container dockmate-ai
```
The app will then be accessible in your browser at `http://localhost:3000`.

### How to run using docker-compose

For an easier setup, you can use Docker Compose to build and run the app in one step:
```bash
docker compose up --build
```
To run it in detached mode (in the background):
```bash
docker compose up -d --build
```

### How to stop the container

If you ran the container using `docker run` (and stopped it using Ctrl+C), you can fully remove it with:
```bash
docker rm dockmate-ai-container
```
If it's still running in the background, stop it first:
```bash
docker stop dockmate-ai-container
docker rm dockmate-ai-container
```

If you used Docker Compose, you can stop and remove the containers with:
```bash
docker compose down
```
