import React, { useEffect, useState, useRef } from "react";

interface HealthStatus {
  status: string;
  service: string;
  mock_mode: boolean;
}

interface EligibilityResult {
  program_type: string;
  likely_eligible: boolean;
  confidence: number;
  income_limit: number;
  fpl_percentage: number;
  factors: string[];
  required_documents: string[];
  next_steps: string[];
}

interface Citation {
  source: string;
  text: string;
  regulation_ref: string | null;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  eligibility?: EligibilityResult | null;
  citations?: Citation[];
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("http://localhost:8003/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8003/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: data.response,
        eligibility: data.eligibility,
        citations: data.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I could not process your request." },
      ]);
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f0f7ff", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{ background: "linear-gradient(135deg, #1a56db, #0e7c47)", color: "white", padding: "16px 24px", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>🏥 Medi-Cal Eligibility Agent</h1>
            <p style={{ margin: "4px 0 0", fontSize: 13, opacity: 0.9 }}>DHCS — AI-Powered Eligibility Screening</p>
          </div>
          <span style={{ fontSize: 12, background: health ? "rgba(255,255,255,0.2)" : "rgba(255,0,0,0.3)", padding: "4px 10px", borderRadius: 12 }}>
            {health ? `✓ Connected (${health.mock_mode ? "mock" : "live"})` : "✗ Offline"}
          </span>
        </div>
      </header>

      {/* Chat Area */}
      <main style={{ maxWidth: 800, margin: "0 auto", padding: 16 }}>
        <div style={{ minHeight: 400, maxHeight: "60vh", overflowY: "auto", marginBottom: 16 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "#666", padding: "60px 20px" }}>
              <p style={{ fontSize: 18 }}>Welcome! Ask me about Medi-Cal eligibility.</p>
              <p style={{ fontSize: 14 }}>Try: &quot;I make $1,500/month and live alone. Am I eligible?&quot;</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom: 12 }}>
              <div style={{
                background: msg.role === "user" ? "#1a56db" : "white",
                color: msg.role === "user" ? "white" : "#333",
                padding: "12px 16px", borderRadius: 12,
                maxWidth: "80%",
                marginLeft: msg.role === "user" ? "auto" : 0,
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              }}>
                <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
              </div>
              {/* Eligibility Card */}
              {msg.eligibility && (
                <div style={{
                  background: msg.eligibility.likely_eligible ? "#ecfdf5" : "#fef2f2",
                  border: `1px solid ${msg.eligibility.likely_eligible ? "#10b981" : "#ef4444"}`,
                  borderRadius: 12, padding: 16, marginTop: 8, maxWidth: "80%",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <span style={{ fontSize: 20 }}>{msg.eligibility.likely_eligible ? "✅" : "❌"}</span>
                    <strong>{msg.eligibility.likely_eligible ? "Likely Eligible" : "May Not Qualify"}</strong>
                    <span style={{ marginLeft: "auto", fontSize: 12, color: "#666" }}>
                      {msg.eligibility.program_type} • {msg.eligibility.fpl_percentage.toFixed(0)}% FPL
                    </span>
                  </div>
                  {msg.eligibility.next_steps.length > 0 && (
                    <div style={{ fontSize: 13 }}>
                      <strong>Next Steps:</strong>
                      <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
                        {msg.eligibility.next_steps.map((s, j) => <li key={j}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ fontSize: 11, color: "#888", marginTop: 4, maxWidth: "80%" }}>
                  {msg.citations.map((c, j) => (
                    <span key={j} style={{ marginRight: 8 }}>📄 {c.source}{c.regulation_ref ? ` (${c.regulation_ref})` : ""}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div style={{ color: "#888", padding: 8 }}>Analyzing...</div>}
          <div ref={messagesEnd} />
        </div>

        {/* Input */}
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about Medi-Cal eligibility..."
            style={{
              flex: 1, padding: "12px 16px", borderRadius: 12,
              border: "1px solid #ccc", fontSize: 15, outline: "none",
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            style={{
              padding: "12px 24px", borderRadius: 12, border: "none",
              background: "#1a56db", color: "white", fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer", fontSize: 15,
            }}
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
