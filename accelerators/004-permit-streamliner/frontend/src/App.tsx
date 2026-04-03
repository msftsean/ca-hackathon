import React, { useRef, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";

export default function App() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-yellow-50 flex flex-col">
      {/* Header */}
      <header
        className="text-white px-6 py-4 shadow-lg"
        style={{ backgroundColor: "#1B2A4A" }}
      >
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg"
            style={{ backgroundColor: "#D4A537", color: "#1B2A4A" }}
          >
            PS
          </div>
          <div>
            <h1 className="text-xl font-bold">Permit Streamliner</h1>
            <p className="text-gray-300 text-xs">
              AI-powered permit intake and routing for California
            </p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-16">
            <h2
              className="text-2xl font-bold mb-2"
              style={{ color: "#1B2A4A" }}
            >
              Welcome to Permit Streamliner
            </h2>
            <p className="text-gray-600 mb-6">
              Ask about building permits, zoning, fees, and application status.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
              {[
                "I want to build an addition",
                "What documents do I need?",
                "Check zoning for my address",
                "How much does a permit cost?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 hover:border-yellow-400 hover:shadow-md transition text-sm text-gray-700"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white rounded-2xl px-4 py-3 border border-gray-200 shadow-sm">
              <div className="flex gap-1">
                <span
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{ backgroundColor: "#D4A537" }}
                />
                <span
                  className="w-2 h-2 rounded-full animate-bounce [animation-delay:0.1s]"
                  style={{ backgroundColor: "#D4A537" }}
                />
                <span
                  className="w-2 h-2 rounded-full animate-bounce [animation-delay:0.2s]"
                  style={{ backgroundColor: "#D4A537" }}
                />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm mb-4">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* Input */}
      <footer className="border-t border-gray-200 bg-white px-4 py-3">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </footer>
    </div>
  );
}
