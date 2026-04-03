import { test, expect } from "@playwright/test";

test.describe("Cross-Agency Knowledge Hub Chat", () => {
  test("should load the chat interface", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Cross-Agency Knowledge Hub")).toBeVisible();
    await expect(
      page.getByText("Welcome to the Knowledge Hub")
    ).toBeVisible();
  });

  test("should show quick action buttons", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("button", { name: /Find CDSS policy/i })
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /expert on procurement/i })
    ).toBeVisible();
  });

  test("should have an input field and search button", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByLabel("Message input")).toBeVisible();
    await expect(page.getByRole("button", { name: "Search" })).toBeVisible();
  });

  test("should send a message and receive a response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByLabel("Message input");
    await input.fill("Find CDSS policy on CalFresh");
    await page.getByRole("button", { name: "Search" }).click();
    await expect(
      page.getByText("Find CDSS policy on CalFresh")
    ).toBeVisible();
  });
});
