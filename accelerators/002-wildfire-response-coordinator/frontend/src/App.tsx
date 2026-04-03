import React, { useEffect, useState } from "react";

interface HealthStatus {
  status: string;
  service: string;
  mock_mode: boolean;
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch("http://localhost:8002/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold text-red-900 mb-4">
          Wildfire Response Coordinator
        </h1>
        <p className="text-gray-600 mb-4">
          AI-powered emergency coordination for CAL FIRE and Cal OES.
        </p>
        {health ? (
          <span className="text-green-600 text-sm">
            ✓ Backend connected ({health.mock_mode ? "mock" : "live"} mode)
          </span>
        ) : (
          <span className="text-red-500 text-sm">✗ Backend unavailable</span>
        )}
      </div>
    </div>
  );
}
