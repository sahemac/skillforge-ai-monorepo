/**
 * AuthService - Authentication and authorization service
 * Handles login, logout, token refresh, and user profile management
 */

import { ApiClient } from '../client/ApiClient';
import type {
  LoginRequest,
  AuthResponse,
  RefreshTokenRequest,
  UserResponse,
  RequestConfig,
} from '../types';

export class AuthService {
  constructor(private apiClient: ApiClient) {}

  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest, config?: RequestConfig): Promise<AuthResponse> {
    const response = await this.apiClient.post<AuthResponse>(
      '/auth/login',
      credentials,
      { ...config, skipAuth: true }
    );

    // Automatically set tokens after successful login
    this.apiClient.setTokens({
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      expiresAt: response.expiresAt,
    });

    return response;
  }

  /**
   * Logout current user
   */
  async logout(config?: RequestConfig): Promise<{ message: string }> {
    try {
      const response = await this.apiClient.post<{ message: string }>('/auth/logout', {}, config);
      return response;
    } finally {
      // Always clear tokens, even if logout request fails
      this.apiClient.clearTokens();
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(
    refreshTokenRequest: RefreshTokenRequest,
    config?: RequestConfig
  ): Promise<AuthResponse> {
    const response = await this.apiClient.post<AuthResponse>(
      '/auth/refresh',
      refreshTokenRequest,
      { ...config, skipAuth: true }
    );

    // Automatically update tokens after successful refresh
    this.apiClient.setTokens({
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      expiresAt: response.expiresAt,
    });

    return response;
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(config?: RequestConfig): Promise<UserResponse> {
    return this.apiClient.get<UserResponse>('/auth/me', undefined, config);
  }

  /**
   * Get current user permissions
   */
  async getUserPermissions(config?: RequestConfig): Promise<string[]> {
    return this.apiClient.get<string[]>('/auth/permissions', undefined, config);
  }

  /**
   * Validate current token
   */
  async validateToken(config?: RequestConfig): Promise<{ valid: boolean; expiresAt: number }> {
    return this.apiClient.get<{ valid: boolean; expiresAt: number }>(
      '/auth/validate',
      undefined,
      config
    );
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(
    email: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/password-reset',
      { email },
      { ...config, skipAuth: true }
    );
  }

  /**
   * Reset password with token
   */
  async resetPassword(
    token: string,
    newPassword: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/password-reset/confirm',
      { token, newPassword },
      { ...config, skipAuth: true }
    );
  }

  /**
   * Change user password
   */
  async changePassword(
    currentPassword: string,
    newPassword: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/change-password',
      { currentPassword, newPassword },
      config
    );
  }

  /**
   * Enable two-factor authentication
   */
  async enableTwoFactor(config?: RequestConfig): Promise<{ qrCode: string; secret: string }> {
    return this.apiClient.post<{ qrCode: string; secret: string }>(
      '/auth/2fa/enable',
      {},
      config
    );
  }

  /**
   * Confirm two-factor authentication setup
   */
  async confirmTwoFactor(
    token: string,
    config?: RequestConfig
  ): Promise<{ backupCodes: string[] }> {
    return this.apiClient.post<{ backupCodes: string[] }>(
      '/auth/2fa/confirm',
      { token },
      config
    );
  }

  /**
   * Disable two-factor authentication
   */
  async disableTwoFactor(
    password: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/2fa/disable',
      { password },
      config
    );
  }

  /**
   * Generate new backup codes
   */
  async generateBackupCodes(config?: RequestConfig): Promise<{ backupCodes: string[] }> {
    return this.apiClient.post<{ backupCodes: string[] }>(
      '/auth/2fa/backup-codes',
      {},
      config
    );
  }

  /**
   * Login with two-factor authentication
   */
  async loginWithTwoFactor(
    credentials: LoginRequest & { twoFactorToken: string },
    config?: RequestConfig
  ): Promise<AuthResponse> {
    const response = await this.apiClient.post<AuthResponse>(
      '/auth/login/2fa',
      credentials,
      { ...config, skipAuth: true }
    );

    // Automatically set tokens after successful login
    this.apiClient.setTokens({
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      expiresAt: response.expiresAt,
    });

    return response;
  }

  /**
   * Verify email address
   */
  async verifyEmail(
    token: string,
    config?: RequestConfig
  ): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/verify-email',
      { token },
      { ...config, skipAuth: true }
    );
  }

  /**
   * Resend email verification
   */
  async resendEmailVerification(config?: RequestConfig): Promise<{ message: string }> {
    return this.apiClient.post<{ message: string }>(
      '/auth/verify-email/resend',
      {},
      config
    );
  }

  /**
   * Get authentication status
   */
  isAuthenticated(): boolean {
    return this.apiClient.isAuthenticated();
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | null {
    return this.apiClient.getAccessToken();
  }

  /**
   * Clear authentication tokens
   */
  clearTokens(): void {
    this.apiClient.clearTokens();
  }

  /**
   * Set authentication tokens manually
   */
  setTokens(tokens: Pick<AuthResponse, 'accessToken' | 'refreshToken' | 'expiresAt'>): void {
    this.apiClient.setTokens(tokens);
  }
}

export default AuthService;