/**
 * SkillForge AI API Client SDK
 * Main entry point for the type-safe API client
 */

import { ApiClient, ApiClientConfig } from './client/ApiClient';
import { AuthService } from './services/AuthService';
import { UsersService } from './services/UsersService';
import { ProjectsService } from './services/ProjectsService';

// Re-export types for external use
export * from './types';
export * from './client/ApiClient';
export * from './services/AuthService';
export * from './services/UsersService';
export * from './services/ProjectsService';

/**
 * Main SkillForge AI SDK class
 * Provides access to all API services with a unified interface
 */
export class SkillForgeSDK {
  private apiClient: ApiClient;
  
  // Service instances
  public readonly auth: AuthService;
  public readonly users: UsersService;
  public readonly projects: ProjectsService;

  constructor(config: ApiClientConfig) {
    this.apiClient = new ApiClient(config);
    
    // Initialize services
    this.auth = new AuthService(this.apiClient);
    this.users = new UsersService(this.apiClient);
    this.projects = new ProjectsService(this.apiClient);
  }

  /**
   * Get the underlying API client instance for advanced usage
   */
  getApiClient(): ApiClient {
    return this.apiClient;
  }

  /**
   * Check if the user is authenticated
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
   * Clear all authentication tokens and cache
   */
  clearSession(): void {
    this.apiClient.clearTokens();
    this.apiClient.clearCache();
  }

  /**
   * Clear API cache
   */
  clearCache(): void {
    this.apiClient.clearCache();
  }
}

/**
 * Create a new SkillForge SDK instance
 */
export function createSkillForgeSDK(config: ApiClientConfig): SkillForgeSDK {
  return new SkillForgeSDK(config);
}

/**
 * Default SDK factory with common configuration
 */
export function createDefaultSDK(options: {
  baseURL?: string;
  timeout?: number;
  onAuthError?: () => void;
  enableCache?: boolean;
  enableLogging?: boolean;
} = {}): SkillForgeSDK {
  const defaultConfig: ApiClientConfig = {
    baseURL: options.baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    timeout: options.timeout || 30000,
    retries: 3,
    retryDelay: 1000,
    enableCache: options.enableCache ?? true,
    cacheTTL: 5 * 60 * 1000, // 5 minutes
    enableRequestLogging: options.enableLogging ?? process.env.NODE_ENV === 'development',
    enableResponseLogging: options.enableLogging ?? process.env.NODE_ENV === 'development',
    onAuthError: options.onAuthError,
  };

  return new SkillForgeSDK(defaultConfig);
}

// Export the main SDK class as default
export default SkillForgeSDK;