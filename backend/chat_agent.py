import os
import json
import logging
from dotenv import load_dotenv
from typing import TypedDict, List, Union
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langchain_core.chat_history import InMemoryChatMessageHistory
from utils.prompt_utils import fill_prompt

# ====== 日志配置 ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ====== 加载 API Key ======
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

# ====== 加载配置 ======
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


# ====== JSON Summary Memory ======
class JSONSummaryBufferMemory:
    def __init__(self, summary_llm):
        self.summary_llm = summary_llm
        self.update_every = CONFIG["memory"]["update_every"]
        self.max_buffer_messages = CONFIG["memory"]["max_buffer_messages"]

        self.buffer_history = InMemoryChatMessageHistory()
        self.summary_json = {"facts": [], "recent_topics": [], "updated": None}
        self.counter = 0

    async def save_context(self, user_input: str, ai_output: str):
        self.buffer_history.add_message(HumanMessage(content=user_input))
        self.buffer_history.add_message(AIMessage(content=ai_output))
        self.counter += 1

        if self.counter % self.update_every == 0:
            await self._update_summary()

    async def _update_summary(self):
        history = self.buffer_history.messages
        if not history:
            return

        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in history])

        # Step 1: 压缩
        compress_prompt = fill_prompt(
            CONFIG["prompts"]["compress_prompt"],
            {"history": history_str}
        )
        compressed = self.summary_llm.invoke([HumanMessage(content=compress_prompt)]).content.strip()
        logger.info(f"[summary] Compressed new messages:\n{compressed}")

        # Step 2: 合并
        merge_prompt = fill_prompt(
            CONFIG["prompts"]["merge_prompt"],
            {
                "summary": json.dumps(self.summary_json, ensure_ascii=False),
                "bullets": compressed
            }
        )
        response = self.summary_llm.invoke([HumanMessage(content=merge_prompt)])
        raw_output = response.content.strip()

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            logger.warning("[summary] Invalid JSON, attempting repair...")
            try:
                from json_repair import repair_json
                fixed_json = repair_json(raw_output)
                parsed = json.loads(fixed_json)
                logger.info("[summary] JSON repaired successfully")
            except Exception as e:
                logger.error(f"[summary] Failed to repair JSON: {e}")
                return

        self.summary_json = parsed
        logger.info(f"[summary] Updated JSON summary: {self.summary_json}")

        self.buffer_history.messages = self.buffer_history.messages[-self.max_buffer_messages:]

    def get_summary(self):
        return self.summary_json

    def load_memory(self):
        """拼接 summary + buffer，供 system prompt 使用"""
        facts = "\n".join([f"- {f['content']}" for f in self.summary_json.get("facts", [])])
        recents = "\n".join(self.summary_json.get("recent_topics", []))
        buffer_str = "\n".join([f"{m.type}: {m.content}" for m in self.buffer_history.messages])

        return f"[Facts]\n{facts}\n\n[Recent Topics]\n{recents}\n\n[Buffer]\n{buffer_str}"

    def clear(self):
        self.buffer_history.clear()
        self.summary_json = {"facts": [], "recent_topics": [], "updated": None}
        self.counter = 0
        logger.info("[memory] Cleared")


# ====== State 类型 ======
class State(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]


# ====== 初始化 LLM ======
chat_llm = ChatOpenAI(model="openai/gpt-4o-mini", api_key=API_KEY, base_url=BASE_URL)
summary_llm = ChatOpenAI(model="openai/gpt-4o-mini", api_key=API_KEY, base_url=BASE_URL)

memory = JSONSummaryBufferMemory(summary_llm=summary_llm)


# ====== Chatbot Node ======
async def chatbot_node(state: State):
    user_message = state["messages"][-1].content

    summary_json = memory.get_summary()
    facts = "\n".join([f"- {f['content']}" for f in summary_json.get("facts", [])])
    recents = "\n".join(summary_json.get("recent_topics", []))
    recent_context = "\n".join([f"{m.type}: {m.content}" for m in memory.buffer_history.messages[-5:]])

    system_prompt = fill_prompt(
        CONFIG["prompts"]["system_prompt"],
        {
            "facts": facts,
            "recents": recents,
            "recent": recent_context
        }
    )

    response = await chat_llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    state["messages"].append(AIMessage(content=response.content))
    return state


# ====== LangGraph 应用 ======
graph = StateGraph(State)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")
app = graph.compile()
