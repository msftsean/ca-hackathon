import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
  },
  webServer: [
    {
      command: "cd ../../backend && USE_MOCK_SERVICES=true uvicorn app.main:app --port 8000",
      port: 8000,
      reuseExistingServer: true,
    },
  ],
});
