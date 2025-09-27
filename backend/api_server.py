import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from langchain.schema import HumanMessage
from chat_agent import app as langgraph_app, memory
import logging

logger = logging.getLogger(__name__)

api = FastAPI()


class ChatRequest(BaseModel):
    message: str


@api.post("/chat")
async def chat(req: ChatRequest):
    return {"status": "ok"}


@api.get("/chat/stream")
async def chat_stream(message: str):
    async def event_stream():
        ai_reply = ""
        state = {"messages": [HumanMessage(content=message)]}

        async for event in langgraph_app.astream_events(state, version="v1"):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                delta = getattr(chunk, "content", None)
                if delta:
                    ai_reply += delta
                    yield f"data: {delta}\n\n"

        yield "event: end\ndata: [DONE]\n\n"

        # 统一在 SSE 结束时保存
        await memory.save_context(message, ai_reply)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@api.get("/summary")
async def get_summary():
    """
    返回记忆的结构化 JSON（facts, recent_topics, updated）
    以及 buffer（最近几条对话）
    """
    summary_json = memory.get_summary()

    buffer_msgs = [
        {"role": msg.type, "content": msg.content}
        for msg in memory.buffer_history.messages
    ]

    return JSONResponse(content={
        "summary": summary_json,
        "buffer": buffer_msgs
    })


@api.post("/new")
def new_chat():
    """清空记忆"""
    memory.clear()
    return {"status": "new chat started"}


if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
