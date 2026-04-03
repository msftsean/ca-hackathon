import { test, expect } from "@playwright/test";

test.describe("BenefitsCal Navigator Chat", () => {
  test("should display welcome page", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=BenefitsCal Navigator")).toBeVisible();
  });

  test("should show suggested questions", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.locator("text=Am I eligible for CalFresh?")
    ).toBeVisible();
  });

  test("should send a message and get response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByLabel("Message input");
    await input.fill("Am I eligible for CalFresh?");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(page.locator("text=Am I eligible for CalFresh?")).toBeVisible();
  });

  test("should have language selector", async ({ page }) => {
    await page.goto("/");
    const select = page.getByLabel("Select language");
    await expect(select).toBeVisible();
  });
});
