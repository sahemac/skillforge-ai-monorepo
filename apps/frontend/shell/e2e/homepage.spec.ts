import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that we're on the homepage
    await expect(page).toHaveURL('/');

    // Check for key elements
    await expect(page.locator('h1, h2')).toBeVisible();
  });

  test('should have correct title', async ({ page }) => {
    await page.goto('/');

    // Check page title
    await expect(page).toHaveTitle(/SkillForge/i);
  });

  test('should display navigation menu', async ({ page }) => {
    await page.goto('/');

    // Check for navigation elements
    const nav = page.locator('nav, header');
    await expect(nav).toBeVisible();
  });

  test('should load static assets', async ({ page }) => {
    // Track failed requests
    const failedRequests: string[] = [];

    page.on('requestfailed', (request) => {
      failedRequests.push(request.url());
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out non-critical failures
    const criticalFailures = failedRequests.filter(
      (url) => !url.includes('analytics') && !url.includes('tracking')
    );

    expect(criticalFailures).toHaveLength(0);
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that content is visible
    await expect(page.locator('body')).toBeVisible();
  });

  test('should have no console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out known non-critical errors
    const criticalErrors = consoleErrors.filter(
      (error) =>
        !error.includes('DevTools') &&
        !error.includes('Extension')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('should perform well', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Page should load in less than 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });
});

test.describe('Navigation', () => {
  test('should navigate to login page', async ({ page }) => {
    await page.goto('/');

    // Find and click login link/button
    const loginButton = page.locator('a[href*="login"], button:has-text("Login"), a:has-text("Login")').first();

    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForLoadState('networkidle');

      // Should be on login page
      await expect(page).toHaveURL(/login/);
    }
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/');

    // Find and click register link/button
    const registerButton = page.locator('a[href*="register"], button:has-text("Register"), a:has-text("Sign up")').first();

    if (await registerButton.isVisible()) {
      await registerButton.click();
      await page.waitForLoadState('networkidle');

      // Should be on register page
      await expect(page).toHaveURL(/register/);
    }
  });

  test('should have working footer links', async ({ page }) => {
    await page.goto('/');

    // Check for footer
    const footer = page.locator('footer');
    if (await footer.isVisible()) {
      // Footer should have links
      const footerLinks = footer.locator('a');
      const count = await footerLinks.count();

      expect(count).toBeGreaterThan(0);
    }
  });
});
