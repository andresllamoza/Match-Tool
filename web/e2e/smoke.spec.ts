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

  test("/customer forwards discovery handoff params to /app", async ({ page }) => {
    await page.goto("/customer?employer=Target&provider=Fidelity");
    await expect(page).toHaveURL(/\/app\?.*employer=Target/);
    await expect(page.getByRole("heading", { name: /can you log in|what type of funds|find your old 401/i })).toBeVisible({
      timeout: 20_000,
    });
  });

  test("/app demo journey completes end-to-end", async ({ page }) => {
    await page.goto("/app");
    await page.getByLabel(/former employer/i).fill("Target");
    await page.getByRole("button", { name: /search for my employer/i }).click();

    await expect(page.getByText(/pensionbee path/i)).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/netbenefits/i)).toBeVisible({ timeout: 15_000 });

    await page.getByRole("button", { name: /yes, i can log in/i }).click();
    await page.getByRole("button", { name: /pre-tax \(traditional ira\)/i }).click();

    await expect(page.getByRole("button", { name: /paper forms/i })).toHaveCount(0);
    await expect(page.getByRole("button", { name: /online/i }).first()).toBeVisible({
      timeout: 15_000,
    });
    await page.getByRole("button", { name: /online/i }).first().click();

    await expect(page.getByText(/netbenefits\.com/i)).toBeVisible({
      timeout: 15_000,
    });

    for (let i = 0; i < 8; i += 1) {
      const done = page.getByRole("button", { name: /done|completed this rollover/i });
      await expect(done).toBeVisible({ timeout: 15_000 });
      await done.click();
    }

    await page.getByRole("button", { name: /confirm transfer started|track my transfer/i }).click();
    await page.getByRole("button", { name: /mark complete/i }).click();

    await expect(page.getByText(/1% match activated/i)).toBeVisible({ timeout: 15_000 });
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
