import { useState, useCallback } from "react";
import type { ChatMessage, ChatRequest, ChatResponse } from "../types";

const API_URL = "http://localhost:8000/api/chat";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string, language = "en", agencyFilter?: string[]) => {
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const body: ChatRequest = { message: text, language };
        if (agencyFilter) body.agency_filter = agencyFilter;

        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });

        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        const data: ChatResponse = await res.json();

        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
          citations: data.citations,
          documents: data.documents ?? undefined,
          experts: data.experts ?? undefined,
          cross_references: data.cross_references ?? undefined,
          confidence: data.confidence,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
