import React, { useRef, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";

export default function App() {
  const { messages, loading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-orange-700 to-red-700 text-white px-4 py-3 shadow-md">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <span className="text-2xl">🚨</span>
          <div>
            <h1 className="text-lg font-bold leading-tight">
              Cal OES Emergency Chatbot
            </h1>
            <p className="text-xs text-orange-200">
              Multilingual emergency information for California
            </p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-12">
              <p className="text-4xl mb-4">🆘</p>
              <p className="text-sm">
                Ask about active alerts, evacuations, shelters, or air quality.
              </p>
              <p className="text-xs text-gray-300 mt-1">
                For life-threatening emergencies, call 911.
              </p>
            </div>
          )}
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && (
            <div className="flex justify-start mb-3">
              <div className="bg-gray-100 rounded-xl px-4 py-3 text-sm text-gray-500 animate-pulse">
                Searching emergency data…
              </div>
            </div>
          )}
          {error && (
            <div className="text-center text-red-500 text-sm py-2">
              Error: {error}
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <div className="max-w-3xl mx-auto w-full">
        <ChatInput onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  );
}
