import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from agent import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
import uvicorn
from generator import generate_docker_config
import json
from db import init_db, get_projects, create_project, get_project, get_messages, add_message

load_dotenv()

app = FastAPI()

# Mount static files for the frontend
os.makedirs("static", exist_ok=True)
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/ui")

# Initialize the database
init_db()

# We will initialize agents dynamically per project, but can keep a fallback
default_agent = create_agent()

class ProjectRequest(BaseModel):
    name: str
    context: str

@app.get("/api/projects")
async def api_get_projects():
    return JSONResponse(get_projects())

@app.post("/api/projects")
async def api_create_project(req: ProjectRequest):
    project = create_project(req.name, req.context)
    return JSONResponse(project)

@app.get("/api/projects/{project_id}/chat")
async def api_get_chat(project_id: int):
    messages = get_messages(project_id)
    return JSONResponse(messages)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/projects/{project_id}/chat")
async def chat(project_id: int, request: ChatRequest):
    try:
        project = get_project(project_id)
        if not project:
            return JSONResponse({"error": "Project not found"}, status_code=404)
            
        # Get past messages
        past_msgs_db = get_messages(project_id)
        langchain_msgs = []
        for msg in past_msgs_db:
            if msg["role"] == "user":
                langchain_msgs.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                langchain_msgs.append(AIMessage(content=msg["content"]))
                
        # Append new message
        user_msg = request.message
        langchain_msgs.append(HumanMessage(content=user_msg))
        
        # Save user message to DB
        add_message(project_id, "user", user_msg)
        
        # Create an agent executor specifically for this project's context
        agent_executor = create_agent(project_name=project["name"], project_context=project["context"])
        
        inputs = {"messages": langchain_msgs}
        final_message = ""
        tool_calls = []
        
        # We use stream but wait for the final message
        for s in agent_executor.stream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if message.type == "ai" and message.content:
                final_message = message.content
            elif message.type == "ai" and hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                     tool_calls.append(tool_call['name'])
                     
        # Save AI response to DB
        tools_str = json.dumps(tool_calls) if tool_calls else None
        add_message(project_id, "ai", final_message, tools_used=tools_str)
                     
        return JSONResponse({
            "response": final_message,
            "tools_used": tool_calls
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

class GenerateRequest(BaseModel):
    description: str

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    try:
        result = generate_docker_config(request.description)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
