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
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-blue-50 flex flex-col">
      {/* Header */}
      <header className="bg-blue-900 text-white px-6 py-4 shadow-lg">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-400 rounded-full flex items-center justify-center text-blue-900 font-bold text-lg">
            KH
          </div>
          <div>
            <h1 className="text-xl font-bold">Cross-Agency Knowledge Hub</h1>
            <p className="text-blue-200 text-xs">
              Federated search across California state government knowledge
              bases
            </p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-16">
            <h2 className="text-2xl font-bold text-blue-900 mb-2">
              Welcome to the Knowledge Hub
            </h2>
            <p className="text-gray-600 mb-6">
              Search policies, find experts, and discover cross-references
              across California state agencies.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
              {[
                "Find CDSS policy on CalFresh",
                "Who is the expert on procurement?",
                "Search across agencies for data governance",
                "What agencies are available?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 hover:border-amber-400 hover:shadow-md transition text-sm text-gray-700"
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
                <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:0.2s]" />
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

