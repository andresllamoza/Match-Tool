import { test, expect } from "@playwright/test";

test.describe("Customer journey smoke", () => {
  test("landing has hero and CTA", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Rollover Companion").first()).toBeVisible();
    await expect(page.getByRole("link", { name: /start my rollover/i })).toBeVisible();
  });

  test("/app loads find step (demo or live API)", async ({ page }) => {
    await page.goto("/app");
    await expect(page.getByRole("button", { name: /save & exit/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /find your old 401/i })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByLabel(/former employer/i)).toBeVisible();
  });

  test("/agent loads BeeKeeper surface", async ({ page }) => {
    await page.goto("/agent");
    await expect(page.getByText(/Internal · BeeKeeper/i)).toBeVisible();
  });

  test("/embed loads widget shell", async ({ page }) => {
    await page.goto("/embed");
    await expect(page.locator("main")).toBeVisible();
  });
});
