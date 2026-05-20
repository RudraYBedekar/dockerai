from langgraph.prebuilt import create_react_agent
import inspect
with open("sig2.txt", "w", encoding="utf-8") as f:
    f.write(str(inspect.signature(create_react_agent)))
