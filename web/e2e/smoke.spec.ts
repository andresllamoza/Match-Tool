import { test, expect, type Locator, type Page } from "@playwright/test";

async function clickJourneyAction(page: Page, locator: Locator) {
  await Promise.all([
    page.waitForResponse((r) => r.url().includes("/action") && r.ok()),
    locator.click(),
  ]);
}

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
    await page.goto("/customer?employer=Target&provider=Alight");
    await expect(page).toHaveURL(/\/app\?.*employer=Target/);
    await expect(page.getByText(/alight/i).first()).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole("heading", { name: /can you log in|what type of funds|find your old 401/i })).toBeVisible({
      timeout: 20_000,
    });
  });

  test("/app demo journey completes end-to-end", async ({ page }) => {
    test.setTimeout(120_000);

    await page.goto("/app");
    await page.getByLabel(/former employer/i).fill("Target");
    await clickJourneyAction(page, page.getByRole("button", { name: /search for my employer/i }));

    await expect(page.getByText(/matched provider/i)).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/alight/i).first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/rollovercentral/i).first()).toBeVisible({ timeout: 15_000 });

    await clickJourneyAction(page, page.getByRole("button", { name: /yes, i can log in/i }));
    await clickJourneyAction(
      page,
      page.getByRole("button", { name: /pre-tax \(traditional ira\)/i })
    );

    await expect(page.getByRole("button", { name: /paper forms/i })).toHaveCount(0);
    await expect(page.getByRole("button", { name: /online/i }).first()).toBeVisible({
      timeout: 15_000,
    });
    await clickJourneyAction(page, page.getByRole("button", { name: /online/i }).first());

    await expect(page.getByText(/alight\.com\/find-your-hr-website/i).first()).toBeVisible({
      timeout: 15_000,
    });

    const stepNext = page.getByRole("button", { name: /^done with this step$/i });
    const stepFinish = page.getByRole("button", { name: /completed this rollover/i });
    await expect(stepNext.or(stepFinish)).toBeVisible({ timeout: 15_000 });

    for (let i = 0; i < 35; i += 1) {
      if (await stepFinish.isVisible()) {
        await clickJourneyAction(page, stepFinish);
        break;
      }
      await expect(stepNext).toBeVisible({ timeout: 15_000 });
      await clickJourneyAction(page, stepNext);
    }

    await clickJourneyAction(
      page,
      page.getByRole("button", { name: /confirm transfer started|track my transfer/i })
    );
    await clickJourneyAction(page, page.getByRole("button", { name: /mark complete/i }));

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
