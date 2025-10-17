// components/ChatPage.jsx
import React, { useState, useRef, useEffect } from "react";
import { askQuestion } from "../api";
import "./ChatPage.css";

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I'm your supplier recommendation assistant. Ask me about finding the best suppliers for your business needs.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = {
      sender: "user",
      text: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await askQuestion(input);
      const botMsg = {
        sender: "bot",
        text: res.data.answer,
        timestamp: new Date(),
        sources: res.data.sources || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const botMsg = {
        sender: "bot",
        text: "Sorry, I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>Supplier Recommendations</h2>
        <p>Ask me about suppliers, pricing, and market insights</p>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender}`}>
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <span className="sources-label">Sources:</span>
                    {message.sources.map((source, idx) => (
                      <span key={idx} className="source-tag">
                        {source}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="message-time">
                {formatTime(message.timestamp)}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message bot loading">
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span>AI is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about suppliers, pricing, recommendations..."
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="send-button"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
