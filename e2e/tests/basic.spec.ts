import { test, expect } from '@playwright/test';

const WEB = process.env.WEB || 'http://localhost:3001';

test('home loads', async ({ page }) => {
  await page.goto(WEB);
  await expect(page.locator('h1')).toContainText(/DoganAI Compliance/i);
});

test('login works', async ({ page }) => {
  await page.goto(WEB + '/(auth)/login');
  await page.getByPlaceholder('Email').fill('admin@example.com');
  await page.getByPlaceholder('Password').fill('admin123');
  await page.getByRole('button').click();
  await expect(page.locator('text=Logged in')).toBeVisible({ timeout: 5000 });
});

test('standards page renders', async ({ page }) => {
  await page.goto(WEB + '/standards');
  await expect(page.locator('h1')).toBeVisible();
});

