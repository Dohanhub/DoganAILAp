import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const WEB = process.env.WEB || 'http://localhost:3001';

test('evidence upload works', async ({ page, context }) => {
  // Preconfigure API base and API key for the UI
  await context.addInitScript(({ base, key }) => {
    localStorage.setItem('apiBase', base);
    localStorage.setItem('apiKey', key);
  }, { base: 'http://localhost:8010', key: 'testkey' });

  await page.goto(WEB + '/evidence');

  // Create a temp file
  const tmp = path.join(process.cwd(), 'e2e', 'fixtures', 'sample.txt');
  fs.mkdirSync(path.dirname(tmp), { recursive: true });
  fs.writeFileSync(tmp, 'sample evidence');

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(tmp);
  await page.getByRole('button', { name: /Upload|رفع/i }).click();
  await expect(page.locator('text=Uploaded')).toBeVisible({ timeout: 5000 });
});

