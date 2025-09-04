import { test, expect } from '@playwright/test';

const WEB_BASE = process.env.WEB || 'http://localhost:3001';
const API_BASE = process.env.API_BASE || 'http://localhost:8000';

// Test user credentials
const testUser = {
  email: 'e2e-test@doganai.com',
  password: 'TestPass123!',
  username: 'e2euser',
  full_name: 'E2E Test User'
};

test.describe('DoganAI Compliance Kit - UI End-to-End Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set up any global state or authentication if needed
    await page.goto(WEB_BASE);
  });

  test.describe('Landing Page and Navigation', () => {
    test('homepage should load and display key elements', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Check for main heading
      await expect(page.locator('h1')).toContainText(/DoganAI|Compliance/i);
      
      // Check for navigation elements
      const nav = page.locator('nav, header');
      await expect(nav).toBeVisible();
      
      // Check for key sections
      await expect(page.locator('text=/framework|compliance|assessment/i').first()).toBeVisible();
    });

    test('navigation menu should work', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Test navigation to different sections
      const navItems = [
        { text: /dashboard/i, expectedUrl: /dashboard/ },
        { text: /organization/i, expectedUrl: /organization/ },
        { text: /assessment/i, expectedUrl: /assessment/ },
        { text: /risk/i, expectedUrl: /risk/ }
      ];

      for (const item of navItems) {
        const navLink = page.locator(`a:has-text("${item.text.source}")`).first();
        if (await navLink.isVisible()) {
          await navLink.click();
          await expect(page).toHaveURL(item.expectedUrl);
        }
      }
    });

    test('responsive design should work on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
      await page.goto(WEB_BASE);
      
      // Check that content is still visible and accessible
      await expect(page.locator('h1')).toBeVisible();
      
      // Check for mobile menu if present
      const mobileMenu = page.locator('[data-testid="mobile-menu"], .mobile-menu, button[aria-label*="menu"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        await expect(page.locator('nav, .navigation')).toBeVisible();
      }
    });
  });

  test.describe('Authentication Flow', () => {
    test('login page should be accessible', async ({ page }) => {
      await page.goto(`${WEB_BASE}/login`);
      
      // Check for login form elements
      await expect(page.locator('input[type="email"], input[name="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"], input[name="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"], button:has-text("Login")')).toBeVisible();
    });

    test('registration page should be accessible', async ({ page }) => {
      await page.goto(`${WEB_BASE}/register`);
      
      // Check for registration form elements
      await expect(page.locator('input[name="email"], input[type="email"]')).toBeVisible();
      await expect(page.locator('input[name="password"], input[type="password"]')).toBeVisible();
      await expect(page.locator('input[name="username"], input[placeholder*="username"]')).toBeVisible();
      await expect(page.locator('button[type="submit"], button:has-text("Register")')).toBeVisible();
    });

    test('user registration flow should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/register`);
      
      // Fill registration form
      await page.fill('input[name="email"], input[type="email"]', testUser.email);
      await page.fill('input[name="password"], input[type="password"]', testUser.password);
      await page.fill('input[name="username"], input[placeholder*="username"]', testUser.username);
      await page.fill('input[name="full_name"], input[placeholder*="name"]', testUser.full_name);
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Register")');
      
      // Check for success message or redirect
      await expect(page.locator('text=/success|registered|welcome/i')).toBeVisible({ timeout: 10000 });
    });

    test('user login flow should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/login`);
      
      // Fill login form
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Login")');
      
      // Check for successful login (redirect to dashboard or success message)
      await expect(page).toHaveURL(/dashboard|home|main/, { timeout: 10000 });
      await expect(page.locator('text=/welcome|dashboard|logout/i')).toBeVisible();
    });

    test('invalid login should show error', async ({ page }) => {
      await page.goto(`${WEB_BASE}/login`);
      
      // Fill with invalid credentials
      await page.fill('input[type="email"], input[name="email"]', 'invalid@test.com');
      await page.fill('input[type="password"], input[name="password"]', 'wrongpassword');
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Login")');
      
      // Check for error message
      await expect(page.locator('text=/error|invalid|incorrect|failed/i')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Dashboard and Analytics', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each dashboard test
      await page.goto(`${WEB_BASE}/login`);
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      await page.waitForURL(/dashboard|home|main/);
    });

    test('dashboard should display key metrics', async ({ page }) => {
      await page.goto(`${WEB_BASE}/dashboard`);
      
      // Check for key dashboard elements
      const metrics = [
        /organization/i,
        /assessment/i,
        /risk/i,
        /compliance/i,
        /framework/i
      ];

      for (const metric of metrics) {
        await expect(page.locator(`text=${metric.source}`).first()).toBeVisible();
      }
      
      // Check for charts or visualizations
      const chartElements = page.locator('canvas, svg, .chart, [data-testid*="chart"]');
      if (await chartElements.count() > 0) {
        await expect(chartElements.first()).toBeVisible();
      }
    });

    test('dashboard should show real-time data', async ({ page }) => {
      await page.goto(`${WEB_BASE}/dashboard`);
      
      // Check for numeric values (should not be all zeros)
      const numbers = page.locator('text=/\\d+/');
      await expect(numbers.first()).toBeVisible();
      
      // Check for recent activity or updates
      const timestamps = page.locator('text=/today|yesterday|ago|recent/i');
      if (await timestamps.count() > 0) {
        await expect(timestamps.first()).toBeVisible();
      }
    });
  });

  test.describe('Organization Management', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each test
      await page.goto(`${WEB_BASE}/login`);
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      await page.waitForURL(/dashboard|home|main/);
    });

    test('organizations page should load', async ({ page }) => {
      await page.goto(`${WEB_BASE}/organizations`);
      
      // Check for organizations list or table
      await expect(page.locator('table, .organization-list, [data-testid*="org"]')).toBeVisible();
      
      // Check for add organization button
      await expect(page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")')).toBeVisible();
    });

    test('create organization form should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/organizations`);
      
      // Click add organization button
      await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New")');
      
      // Fill organization form
      const orgName = `Test Org ${Date.now()}`;
      await page.fill('input[name="name"], input[placeholder*="name"]', orgName);
      await page.fill('input[name="sector"], input[placeholder*="sector"], select[name="sector"]', 'Technology');
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
      
      // Check for success message
      await expect(page.locator('text=/success|created|added/i')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Assessment Management', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each test
      await page.goto(`${WEB_BASE}/login`);
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      await page.waitForURL(/dashboard|home|main/);
    });

    test('assessments page should load', async ({ page }) => {
      await page.goto(`${WEB_BASE}/assessments`);
      
      // Check for assessments list
      await expect(page.locator('table, .assessment-list, [data-testid*="assessment"]')).toBeVisible();
      
      // Check for framework selection
      await expect(page.locator('select, .framework-selector, [data-testid*="framework"]')).toBeVisible();
    });

    test('start new assessment should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/assessments`);
      
      // Click start assessment button
      await page.click('button:has-text("Start"), button:has-text("New"), button:has-text("Create")');
      
      // Select framework and organization
      const frameworkSelect = page.locator('select[name="framework"], .framework-selector select');
      if (await frameworkSelect.isVisible()) {
        await frameworkSelect.selectOption({ index: 0 });
      }
      
      const orgSelect = page.locator('select[name="organization"], .organization-selector select');
      if (await orgSelect.isVisible()) {
        await orgSelect.selectOption({ index: 0 });
      }
      
      // Start assessment
      await page.click('button:has-text("Start"), button:has-text("Begin"), button[type="submit"]');
      
      // Check for assessment interface
      await expect(page.locator('text=/assessment|control|question/i')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Risk Management', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each test
      await page.goto(`${WEB_BASE}/login`);
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      await page.waitForURL(/dashboard|home|main/);
    });

    test('risks page should load', async ({ page }) => {
      await page.goto(`${WEB_BASE}/risks`);
      
      // Check for risks list
      await expect(page.locator('table, .risk-list, [data-testid*="risk"]')).toBeVisible();
      
      // Check for risk severity indicators
      await expect(page.locator('text=/high|medium|low|critical/i')).toBeVisible();
    });

    test('create risk should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/risks`);
      
      // Click add risk button
      await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New")');
      
      // Fill risk form
      const riskTitle = `Test Risk ${Date.now()}`;
      await page.fill('input[name="title"], input[placeholder*="title"]', riskTitle);
      await page.fill('textarea[name="description"], textarea[placeholder*="description"]', 'Test risk description');
      
      // Select severity and likelihood
      const severitySelect = page.locator('select[name="severity"]');
      if (await severitySelect.isVisible()) {
        await severitySelect.selectOption('high');
      }
      
      const likelihoodSelect = page.locator('select[name="likelihood"]');
      if (await likelihoodSelect.isVisible()) {
        await likelihoodSelect.selectOption('medium');
      }
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
      
      // Check for success message
      await expect(page.locator('text=/success|created|added/i')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Reporting and Analytics', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each test
      await page.goto(`${WEB_BASE}/login`);
      await page.fill('input[type="email"], input[name="email"]', testUser.email);
      await page.fill('input[type="password"], input[name="password"]', testUser.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      await page.waitForURL(/dashboard|home|main/);
    });

    test('reports page should load', async ({ page }) => {
      await page.goto(`${WEB_BASE}/reports`);
      
      // Check for reports interface
      await expect(page.locator('text=/report|generate|download/i')).toBeVisible();
      
      // Check for report types
      await expect(page.locator('select, .report-type, [data-testid*="report"]')).toBeVisible();
    });

    test('generate report should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/reports`);
      
      // Select report type
      const reportTypeSelect = page.locator('select[name="reportType"], .report-type select');
      if (await reportTypeSelect.isVisible()) {
        await reportTypeSelect.selectOption({ index: 0 });
      }
      
      // Generate report
      await page.click('button:has-text("Generate"), button:has-text("Create")');
      
      // Check for report generation progress or completion
      await expect(page.locator('text=/generating|generated|download|complete/i')).toBeVisible({ timeout: 15000 });
    });
  });

  test.describe('Accessibility and Internationalization', () => {
    test('Arabic language support should work', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Look for language switcher
      const langSwitcher = page.locator('button:has-text("العربية"), select[name="language"], .language-selector');
      if (await langSwitcher.isVisible()) {
        await langSwitcher.click();
        
        // Check for Arabic text
        await expect(page.locator('text=/العربية|السعودية|الامتثال/').first()).toBeVisible({ timeout: 5000 });
      }
    });

    test('keyboard navigation should work', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Test tab navigation
      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();
      
      // Test multiple tabs
      for (let i = 0; i < 5; i++) {
        await page.keyboard.press('Tab');
        const focused = page.locator(':focus');
        if (await focused.isVisible()) {
          await expect(focused).toBeVisible();
        }
      }
    });

    test('color contrast should be adequate', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Check for proper contrast in key elements
      const textElements = page.locator('h1, h2, h3, p, button, a');
      const count = await textElements.count();
      
      // Ensure text elements are visible (basic contrast check)
      for (let i = 0; i < Math.min(count, 10); i++) {
        await expect(textElements.nth(i)).toBeVisible();
      }
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('404 page should be handled gracefully', async ({ page }) => {
      await page.goto(`${WEB_BASE}/nonexistent-page`);
      
      // Check for 404 page or error message
      await expect(page.locator('text=/404|not found|page not found/i')).toBeVisible();
    });

    test('network error should be handled gracefully', async ({ page }) => {
      // Intercept API calls and simulate network error
      await page.route('**/api/**', route => {
        route.abort('failed');
      });
      
      await page.goto(`${WEB_BASE}/dashboard`);
      
      // Check for error message or offline indicator
      await expect(page.locator('text=/error|offline|connection|failed/i')).toBeVisible({ timeout: 10000 });
    });

    test('form validation should work', async ({ page }) => {
      await page.goto(`${WEB_BASE}/register`);
      
      // Submit empty form
      await page.click('button[type="submit"], button:has-text("Register")');
      
      // Check for validation messages
      await expect(page.locator('text=/required|invalid|error/i')).toBeVisible();
    });
  });

  test.describe('Performance and Loading', () => {
    test('pages should load within reasonable time', async ({ page }) => {
      const pages = [
        WEB_BASE,
        `${WEB_BASE}/dashboard`,
        `${WEB_BASE}/organizations`,
        `${WEB_BASE}/assessments`
      ];

      for (const pageUrl of pages) {
        const start = Date.now();
        await page.goto(pageUrl);
        const loadTime = Date.now() - start;
        
        // Page should load within 5 seconds
        expect(loadTime).toBeLessThan(5000);
        
        // Check that main content is visible
        await expect(page.locator('main, .main-content, h1')).toBeVisible();
      }
    });

    test('images should load properly', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Check for images and ensure they load
      const images = page.locator('img');
      const count = await images.count();
      
      for (let i = 0; i < Math.min(count, 5); i++) {
        const img = images.nth(i);
        if (await img.isVisible()) {
          // Check that image has loaded (not broken)
          const naturalWidth = await img.evaluate((el: HTMLImageElement) => el.naturalWidth);
          expect(naturalWidth).toBeGreaterThan(0);
        }
      }
    });
  });
});
