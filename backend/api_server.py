# backend/api_server.py
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from langchain.schema import HumanMessage
from chat_agent import app as langgraph_app, memory

api = FastAPI()

class ChatRequest(BaseModel):
    message: str

@api.post("/chat")
async def chat(req: ChatRequest):
    state = {"messages": [HumanMessage(content=req.message)]}
    result = await langgraph_app.ainvoke(state)
    reply = result["messages"][-1].content
    return {"reply": reply}

@api.get("/summary")
def get_summary():
    return {"summary": memory.load_memory()}

@api.post("/new")
def new_chat():
    memory.clear()
    return {"status": "new chat started"}

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
