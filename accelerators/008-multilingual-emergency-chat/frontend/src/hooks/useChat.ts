import { useState, useCallback } from "react";
import type { ChatMessage, ChatResponse } from "../types";

const API_URL = "http://localhost:8000/api/chat";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string, language: string = "en") => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, language }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: ChatResponse = await res.json();

        const botMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.response,
          data,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const clearMessages = useCallback(() => setMessages([]), []);

  return { messages, loading, error, sendMessage, clearMessages };
}
