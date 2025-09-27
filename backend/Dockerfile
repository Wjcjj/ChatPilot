FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只复制源码，而不是整个开发目录
COPY chat_agent.py api_server.py .

# 在容器里运行时，summary.txt 会写在 /app/data
RUN mkdir -p /app/data
ENV SUMMARY_FILE=/app/data/summary.txt

CMD ["uvicorn", "api_server:api", "--host", "0.0.0.0", "--port", "8000"]
