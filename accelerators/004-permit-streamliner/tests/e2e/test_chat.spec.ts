import { test, expect } from "@playwright/test";

test.describe("Permit Streamliner Chat", () => {
  test("should display welcome page", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=Permit Streamliner")).toBeVisible();
  });

  test("should show suggested questions", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.locator("text=I want to build an addition")
    ).toBeVisible();
  });

  test("should send a message and get response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByLabel("Message input");
    await input.fill("I want to build an addition");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(
      page.locator("text=I want to build an addition")
    ).toBeVisible();
  });

  test("should display permit-themed UI", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=AI-powered permit")).toBeVisible();
  });
});
