import json
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class RunConfig(BaseModel):
    container_name: str = Field(description="Name for the docker container")
    ports: Dict[str, Any] = Field(description="Port mappings, e.g., {'8000/tcp': 8000}")
    environment: Dict[str, Any] = Field(description="Environment variables")
    command: str = Field(description="Command to run the container, if any", default="")

class DockerConfigResponse(BaseModel):
    project_type: str = Field(description="Detected project type/tech stack")
    base_image: str = Field(description="Appropriate base Docker image")
    dockerfile: str = Field(description="The complete Dockerfile content")
    run_config: RunConfig = Field(description="Docker run configuration details")

def generate_docker_config(description: str) -> dict:
    """
    Analyzes a project description and generates a Docker configuration.
    """
    llm = ChatOpenAI(model="meta/llama-3.1-70b-instruct")
    
    parser = PydanticOutputParser(pydantic_object=DockerConfigResponse)
    
    prompt_template = """You are an AI DevOps assistant.

Your task is to analyze a user's project or description and automatically:
1. Detect the project type / tech stack
2. Generate an appropriate Dockerfile
3. Generate Docker run configuration

## Supported Project Types
- Node.js (Express, Vite, React)
- Python (Flask, FastAPI, Django)
- Java (Spring Boot)
- Static frontend (HTML, CSS, JS)
- Others (fallback: generic Linux container)

## Rules
- Always infer the correct base image:
  - Node -> node:18
  - Python -> python:3.10
  - Java -> openjdk:17
  - Static -> nginx:alpine
- Always include a working Dockerfile
- Expose correct ports:
  - Node/React -> 3000
  - FastAPI/Flask -> 8000
  - Django -> 8000
  - Spring Boot -> 8080
  - Nginx -> 80
- Use WORKDIR /app
- Copy files and install dependencies
- Add CMD or ENTRYPOINT
- If unclear, make best assumption

## Formatting Instructions
{format_instructions}

## User Project Description
{description}

Generate the configuration:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["description"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"description": description})
        return result.dict()
    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        # Fallback to direct call with JSON enforcing
        # If it failed to parse, we might need a more robust JSON extraction
        raise Exception(f"Failed to generate valid JSON: {e}")
