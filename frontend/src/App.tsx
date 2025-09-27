import React, { useState, useEffect, useRef } from "react";
import "./index.css";

export default function ChatApp() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [summaryData, setSummaryData] = useState<any>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userInput = input;
    setInput("");

    setMessages((msgs) => [...msgs, { role: "user", content: userInput }, { role: "assistant", content: "" }]);
    setLoading(true);

    await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userInput }),
    });

    const evtSource = new EventSource(`/api/chat/stream?message=${encodeURIComponent(userInput)}`);
    evtSource.onmessage = (event) => {
      setLoading(true);
      const delta = event.data;
      setMessages((msgs) => {
        const updated = [...msgs];
        updated[updated.length - 1] = {
          role: "assistant",
          content: (updated[updated.length - 1]?.content || "") + delta,
        };
        return updated;
      });
    };
    evtSource.addEventListener("end", () => {
      evtSource.close();
      setLoading(false);
    });
    evtSource.onerror = () => {
      console.error("SSE error");
      evtSource.close();
      setLoading(false);
    };
  };

  const fetchSummary = async () => {
    const res = await fetch("/api/summary");
    const data = await res.json();
    setSummaryData(data);
  };

  const clearMemory = async () => {
    await fetch("/api/new", { method: "POST" });
    setMessages([]);
    setSummaryData(null);
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="app-container">
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}
          >
            {msg.content}
          </div>
        ))}

        {loading && (
          <div className="chat-assistant typing-indicator">
            <span>●</span>
            <span>●</span>
            <span>●</span>
          </div>
        )}

        <div ref={chatEndRef}></div>
      </div>

      <div className="input-row">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          className="chat-input"
          placeholder="Type your message... (Shift+Enter for newline)"
          rows={2}
        />
        <button onClick={sendMessage} className="btn btn-primary" disabled={loading}>
          Send
        </button>
      </div>

      <div className="button-row">
        <button onClick={fetchSummary} className="btn btn-secondary">
          查看记忆
        </button>
        <button onClick={clearMemory} className="btn btn-danger">
          清空记忆
        </button>
      </div>

      {summaryData && (
        <pre className="summary-box">
          {JSON.stringify(summaryData, null, 2)}
        </pre>
      )}
    </div>
  );
}
