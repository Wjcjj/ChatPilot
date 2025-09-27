# 🚀 MemoGraph

> An intelligent chat application built with **LangGraph** and **LangChain**, featuring hybrid memory, voice I/O, RAG, and tool calling.



## 📛 Badges

<p align="left">
  <!-- Python -->
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python" />
  <!-- React -->
  <img src="https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white" alt="React" />
  <!-- Docker -->
  <img src="https://img.shields.io/badge/Docker-Ready-2496ed?logo=docker&logoColor=white" alt="Docker" />
  <!-- LangChain -->
  <img src="https://img.shields.io/badge/LangChain-Agent-green?logo=openai&logoColor=white" alt="LangChain" />
  <!-- License -->
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  <!-- GitHub stars -->
  <img src="https://img.shields.io/github/stars/Wjcjj/ChatPilot?style=social" alt="GitHub stars" />
</p>

---

## ✨ Features

- 🧠 **Hybrid Memory System** — Combines short-term buffer memory and long-term summary memory.
- ⚡ **LangGraph-powered Agent** — Flexible graph-based conversation flow.
- 💻 **React + Vite Frontend** — Simple and modern chat UI.
- 🐳 **Dockerized Deployment** — Easy to run in both dev and prod environments.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain, LangGraph
- **Frontend**: React, Vite, TailwindCSS
- **Infra**: Docker & Docker Compose

---

## 🚀 Quick Start

### Development
```bash
# Start dev environment
docker-compose -f docker-compose.dev.yml up

Backend → http://localhost:8000/docs

Frontend → http://localhost:5173
```
### Production
```bash
docker-compose -f docker-compose.yml up --build -d

Frontend → http://localhost:5173

Backend → http://localhost:8000/docs
```

## 📌 Roadmap

- [ ] 🎤 Voice Input — 支持语音输入对话
- [ ] 🔊 Voice Output — 支持语音合成输出
- [ ] 📚 RAG (Retrieval-Augmented Generation) — 接入外部知识库增强回答
- [ ] 🛠️ Tool Calling — 支持调用外部工具/插件

 
## 📄 License

MIT © 2025