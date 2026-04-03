import { test, expect } from "@playwright/test";

test.describe("EDD Claims Assistant Chat", () => {
  test("should load the chat interface", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("EDD Claims Assistant")).toBeVisible();
    await expect(
      page.getByText("Welcome to the EDD Claims Assistant")
    ).toBeVisible();
  });

  test("should show quick action buttons", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("button", { name: /Check my unemployment/i })
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /eligible for disability/i })
    ).toBeVisible();
  });

  test("should have an input field and send button", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByLabel("Message input")).toBeVisible();
    await expect(page.getByRole("button", { name: "Send" })).toBeVisible();
  });

  test("should send a message and receive a response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByLabel("Message input");
    await input.fill("Check my unemployment claim status");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(
      page.getByText("Check my unemployment claim status")
    ).toBeVisible();
  });
});
