# backend/chat_agent.py
import os
import asyncio
from dotenv import load_dotenv
from typing import TypedDict, List, Union
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

# ====== 改良版 SummaryBufferMemory ======
from typing import List
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class FastSummaryBufferMemory:
    def __init__(self, chat_llm, summary_llm=None, update_every=3, max_buffer_messages=5):
        self.chat_llm = chat_llm
        self.summary_llm = summary_llm or chat_llm
        self.update_every = update_every
        self.max_buffer_messages = max_buffer_messages

        # 存储短期对话（Buffer）
        self.buffer_history = InMemoryChatMessageHistory()

        # 存储摘要（长期记忆）
        self.summary_history = InMemoryChatMessageHistory()

        self.counter = 0

    async def save_context(self, user_input: str, ai_output: str):
        """保存一轮对话，并周期性更新摘要"""
        self.buffer_history.add_message(HumanMessage(content=user_input))
        self.buffer_history.add_message(AIMessage(content=ai_output))
        self.counter += 1

        if self.counter % self.update_every == 0:
            await self._update_summary()

    async def _update_summary(self):
        """压缩 Buffer 成摘要，存到 summary"""
        history = self.buffer_history.messages
        if not history:
            return

        # 拼接成纯文本
        history_str = "\n".join(
            [f"{msg.type}: {msg.content}" for msg in history]
        )

        # 用 LLM 做总结
        prompt = f"Summarize the following conversation:\n\n{history_str}\n\nSummary:"
        response = self.summary_llm.invoke([HumanMessage(content=prompt)])

        # 保存摘要
        self.summary_history.add_message(AIMessage(content=response.content))

        # 保留最近 N 条消息
        self.buffer_history.messages = self.buffer_history.messages[-self.max_buffer_messages:]

    def load_memory(self) -> str:
        """获取完整记忆（摘要 + 最近对话）"""
        buffer_str = "\n".join([f"{m.type}: {m.content}" for m in self.buffer_history.messages])
        summary_str = "\n".join([m.content for m in self.summary_history.messages])

        return f"[Summary]\n{summary_str}\n\n[Recent Conversation]\n{buffer_str}"

    def clear(self):
        """清空记忆"""
        self.buffer_history.clear()
        self.summary_history.clear()
        self.counter = 0

# ====== State ======
class State(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]


# ====== LLMs ======
chat_llm = ChatOpenAI(model="openai/gpt-4o-mini", api_key=API_KEY, base_url=BASE_URL)
summary_llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=API_KEY, base_url=BASE_URL)

memory = FastSummaryBufferMemory(chat_llm=chat_llm, summary_llm=summary_llm)

# ====== Chatbot Node ======
async def chatbot_node(state: State):
    memory_context = memory.load_memory()
    user_message = state["messages"][-1].content
    prompt = f"You are a helpful assistant.\n\n{memory_context}\n\nUser: {user_message}"
    response = chat_llm.invoke([HumanMessage(content=prompt)])
    await memory.save_context(user_message, response.content)
    state["messages"].append(AIMessage(content=response.content))
    return state

# ====== LangGraph App ======
graph = StateGraph(State)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")
app = graph.compile()
