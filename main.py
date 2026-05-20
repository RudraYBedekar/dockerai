import os
from dotenv import load_dotenv
from agent import create_agent
from langchain_core.messages import HumanMessage

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    # Check for API key if using OpenAI default
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. The agent will fail unless you're using a local LLM or have set it elsewhere.")
        print("Please configure your .env file.")
        
    print("Initializing Agentic RAG pipeline...")
    agent_executor = create_agent()
    
    print("\n" + "="*50)
    print("DevOps Agent Ready!")
    print("Ask me about your Docker containers or Kubernetes clusters.")
    print("Type 'exit' or 'quit' to stop.")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            # Run the agent graph and stream the responses
            print("\nAgent is thinking...")
            for s in agent_executor.stream(inputs, stream_mode="values"):
                message = s["messages"][-1]
                # Only print the final AI response (or an AI response that doesn't just have tool_calls)
                if message.type == "ai" and message.content:
                    print(f"\nAssistant:\n{message.content}")
                elif message.type == "ai" and hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                         print(f"\n[Agent decided to call tool: {tool_call['name']}]")
                elif message.type == "tool":
                    print(f"\n[Tool Execution Completed: {message.name}]")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
