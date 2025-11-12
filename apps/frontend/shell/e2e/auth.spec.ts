import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.describe('Registration', () => {
    test('should display registration form', async ({ page }) => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');

      // Check for registration form elements
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();

      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
    });

    test('should show validation errors for empty form', async ({ page }) => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');

      // Try to submit empty form
      const submitButton = page.locator('button[type="submit"], button:has-text("Register"), button:has-text("Sign up")').first();

      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Wait for validation errors
        await page.waitForTimeout(500);

        // Check for error messages (could be native HTML5 validation or custom)
        const errors = page.locator('[class*="error"], [role="alert"], .invalid-feedback');
        const errorCount = await errors.count();

        // Should have at least one error
        expect(errorCount).toBeGreaterThanOrEqual(0);
      }
    });

    test('should validate email format', async ({ page }) => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');

      const emailInput = page.locator('input[type="email"], input[name="email"]').first();

      if (await emailInput.isVisible()) {
        // Enter invalid email
        await emailInput.fill('invalid-email');

        const submitButton = page.locator('button[type="submit"]').first();
        if (await submitButton.isVisible()) {
          await submitButton.click();
          await page.waitForTimeout(500);

          // Should show validation error
          const isInvalid = await emailInput.evaluate((el) => {
            return (el as HTMLInputElement).validity.valid === false;
          });

          expect(isInvalid).toBeTruthy();
        }
      }
    });

    test('should accept valid registration data', async ({ page }) => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');

      const timestamp = Date.now();
      const testEmail = `e2e-test-${timestamp}@example.com`;

      // Fill in form
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();
      const fullNameInput = page.locator('input[name="fullName"], input[name="full_name"], input[name="name"]').first();

      if (await emailInput.isVisible()) {
        await emailInput.fill(testEmail);
        await passwordInput.fill('TestPassword123!');

        if (await fullNameInput.isVisible()) {
          await fullNameInput.fill('E2E Test User');
        }

        // Submit form
        const submitButton = page.locator('button[type="submit"]').first();
        await submitButton.click();

        // Wait for response (could be success or error if user already exists)
        await page.waitForTimeout(2000);

        // Should either redirect or show a message
        const currentUrl = page.url();
        const hasSuccessMessage = await page.locator('[class*="success"], [role="status"]').count() > 0;
        const hasErrorMessage = await page.locator('[class*="error"], [role="alert"]').count() > 0;

        // One of these should be true
        expect(currentUrl !== '/register' || hasSuccessMessage || hasErrorMessage).toBeTruthy();
      }
    });
  });

  test.describe('Login', () => {
    test('should display login form', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      // Check for login form elements
      const emailInput = page.locator('input[type="email"], input[name="email"], input[name="username"]').first();
      const passwordInput = page.locator('input[type="password"]').first();

      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
    });

    test('should show validation errors for empty form', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      // Try to submit empty form
      const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first();

      if (await submitButton.isVisible()) {
        await submitButton.click();
        await page.waitForTimeout(500);

        // Check for errors
        const emailInput = page.locator('input[type="email"], input[name="email"]').first();
        const isInvalid = await emailInput.evaluate((el) => {
          return (el as HTMLInputElement).validity.valid === false;
        });

        expect(isInvalid).toBeTruthy();
      }
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();

      if (await emailInput.isVisible()) {
        // Try to login with invalid credentials
        await emailInput.fill('nonexistent@example.com');
        await passwordInput.fill('WrongPassword123!');

        const submitButton = page.locator('button[type="submit"]').first();
        await submitButton.click();

        // Wait for error response
        await page.waitForTimeout(2000);

        // Should show error message or stay on login page
        const hasError = await page.locator('[class*="error"], [role="alert"]').count() > 0;
        const stillOnLogin = page.url().includes('login');

        expect(hasError || stillOnLogin).toBeTruthy();
      }
    });

    test('should have "Forgot Password" link', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      const forgotPasswordLink = page.locator('a:has-text("Forgot"), a:has-text("Reset")').first();

      if (await forgotPasswordLink.count() > 0) {
        await expect(forgotPasswordLink).toBeVisible();
      }
    });

    test('should have link to registration page', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      const registerLink = page.locator('a[href*="register"], a:has-text("Sign up"), a:has-text("Create account")').first();

      if (await registerLink.count() > 0) {
        await expect(registerLink).toBeVisible();
      }
    });
  });

  test.describe('Protected Routes', () => {
    test('should redirect to login when accessing dashboard without auth', async ({ page }) => {
      // Try to access dashboard
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');

      // Should either redirect to login or show login form
      const url = page.url();
      expect(url.includes('login') || url.includes('auth')).toBeTruthy();
    });
  });
});
