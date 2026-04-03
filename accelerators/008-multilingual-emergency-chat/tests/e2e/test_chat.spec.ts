import { test, expect } from "@playwright/test";

test.describe("008 Emergency Chat E2E", () => {
  test("health endpoint returns healthy", async ({ request }) => {
    const resp = await request.get("http://localhost:8000/health");
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body.status).toBe("healthy");
  });

  test("chat API accepts a message", async ({ request }) => {
    const resp = await request.post("http://localhost:8000/api/chat", {
      data: { message: "Are there any alerts?", language: "en" },
    });
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body.response).toBeTruthy();
    expect(body.confidence).toBeGreaterThan(0);
  });

  test("status endpoint returns service info", async ({ request }) => {
    const resp = await request.get("http://localhost:8000/api/status");
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body.service).toBe("multilingual-emergency-chat");
  });
});
