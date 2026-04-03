import React, { useEffect, useState, useRef } from "react";

interface HealthStatus {
  status: string;
  service: string;
  mock_mode: boolean;
}

interface IncidentSummary {
  incident_id: string;
  name: string;
  incident_type: string;
  severity: string;
  location: string;
  containment_pct: number | null;
  status: string;
  lead_agency: string;
}

interface EvacZone {
  zone_id: string;
  zone_name: string;
  status: string;
  population: number;
  routes: string[];
  shelters: string[];
}

interface EvacInfo {
  zones: EvacZone[];
  total_evacuated: number;
  shelters_open: number;
}

interface Resource {
  resource_id: string;
  resource_type: string;
  quantity: number;
  agency: string;
  status: string;
}

interface Citation {
  source: string;
  text: string;
  agency: string | null;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  incident?: IncidentSummary | null;
  evacuation?: EvacInfo | null;
  resources?: Resource[] | null;
  citations?: Citation[];
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("http://localhost:8002/health")
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
      const res = await fetch("http://localhost:8002/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: data.response,
        incident: data.incident,
        evacuation: data.evacuation,
        resources: data.resources,
        citations: data.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Communication error. Check system connectivity." },
      ]);
    }
    setLoading(false);
  };

  const severityColor = (s: string) => {
    const map: Record<string, string> = { minor: "#22c55e", moderate: "#f59e0b", major: "#ef4444", catastrophic: "#7c3aed" };
    return map[s] || "#888";
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#1a1a2e", color: "#e0e0e0", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{ background: "linear-gradient(135deg, #991b1b, #b91c1c, #7f1d1d)", color: "white", padding: "16px 24px", boxShadow: "0 2px 8px rgba(0,0,0,0.4)" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>🔥 Wildfire Response Coordinator</h1>
            <p style={{ margin: "4px 0 0", fontSize: 13, opacity: 0.9 }}>CAL FIRE / Cal OES — Emergency Coordination</p>
          </div>
          <span style={{ fontSize: 12, background: health ? "rgba(255,255,255,0.2)" : "rgba(255,0,0,0.5)", padding: "4px 10px", borderRadius: 12 }}>
            {health ? `✓ Online (${health.mock_mode ? "mock" : "live"})` : "✗ Offline"}
          </span>
        </div>
      </header>

      {/* Chat Area */}
      <main style={{ maxWidth: 900, margin: "0 auto", padding: 16 }}>
        <div style={{ minHeight: 400, maxHeight: "60vh", overflowY: "auto", marginBottom: 16 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "#888", padding: "60px 20px" }}>
              <p style={{ fontSize: 18 }}>Emergency Coordination Console</p>
              <p style={{ fontSize: 14 }}>Try: &quot;What are the active incidents?&quot; or &quot;Show evacuation zones&quot;</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom: 12 }}>
              <div style={{
                background: msg.role === "user" ? "#b91c1c" : "#2d2d44",
                color: "white",
                padding: "12px 16px", borderRadius: 12,
                maxWidth: "85%",
                marginLeft: msg.role === "user" ? "auto" : 0,
                boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
              }}>
                <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
              </div>
              {/* Incident Card */}
              {msg.incident && (
                <div style={{ background: "#2d2d44", border: `2px solid ${severityColor(msg.incident.severity)}`, borderRadius: 12, padding: 16, marginTop: 8, maxWidth: "85%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: severityColor(msg.incident.severity), display: "inline-block" }} />
                    <strong>{msg.incident.name}</strong>
                    <span style={{ marginLeft: "auto", fontSize: 12, color: "#aaa" }}>{msg.incident.incident_id}</span>
                  </div>
                  <div style={{ fontSize: 13, color: "#ccc" }}>
                    {msg.incident.location} • {msg.incident.severity.toUpperCase()} • {msg.incident.containment_pct ?? 0}% contained • {msg.incident.lead_agency}
                  </div>
                </div>
              )}
              {/* Resources Table */}
              {msg.resources && msg.resources.length > 0 && (
                <div style={{ background: "#2d2d44", borderRadius: 12, padding: 12, marginTop: 8, maxWidth: "85%", fontSize: 13 }}>
                  <strong>Resources:</strong>
                  <table style={{ width: "100%", marginTop: 4, borderCollapse: "collapse" }}>
                    <thead><tr style={{ borderBottom: "1px solid #444", color: "#aaa" }}>
                      <th style={{ textAlign: "left", padding: 4 }}>ID</th>
                      <th style={{ textAlign: "left", padding: 4 }}>Type</th>
                      <th style={{ textAlign: "left", padding: 4 }}>Agency</th>
                      <th style={{ textAlign: "left", padding: 4 }}>Status</th>
                    </tr></thead>
                    <tbody>{msg.resources.map((r, j) => (
                      <tr key={j} style={{ borderBottom: "1px solid #333" }}>
                        <td style={{ padding: 4 }}>{r.resource_id}</td>
                        <td style={{ padding: 4 }}>{r.resource_type}</td>
                        <td style={{ padding: 4 }}>{r.agency}</td>
                        <td style={{ padding: 4 }}>{r.status}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              )}
              {/* Evacuation Info */}
              {msg.evacuation && (
                <div style={{ background: "#2d2d44", border: "1px solid #ef4444", borderRadius: 12, padding: 12, marginTop: 8, maxWidth: "85%", fontSize: 13 }}>
                  <strong>🚨 Evacuation: {msg.evacuation.total_evacuated.toLocaleString()} evacuated, {msg.evacuation.shelters_open} shelters open</strong>
                </div>
              )}
              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ fontSize: 11, color: "#666", marginTop: 4, maxWidth: "85%" }}>
                  {msg.citations.map((c, j) => (
                    <span key={j} style={{ marginRight: 8 }}>📋 {c.source}{c.agency ? ` (${c.agency})` : ""}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div style={{ color: "#888", padding: 8 }}>Processing...</div>}
          <div ref={messagesEnd} />
        </div>

        {/* Input */}
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Report incident, request resources, check weather..."
            style={{
              flex: 1, padding: "12px 16px", borderRadius: 12,
              border: "1px solid #444", background: "#2d2d44",
              color: "white", fontSize: 15, outline: "none",
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            style={{
              padding: "12px 24px", borderRadius: 12, border: "none",
              background: "#b91c1c", color: "white", fontWeight: 600,
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
