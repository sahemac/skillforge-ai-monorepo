/**
 * ApiClient - Main API client with interceptors and token management
 * Provides type-safe HTTP client with automatic retries, caching, and error handling
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError,
  InternalAxiosRequestConfig 
} from 'axios';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { 
  ApiError, 
  ApiResponse, 
  RequestConfig,
  ApiNetworkError,
  ApiAuthenticationError,
  ApiAuthorizationError,
  ApiRateLimitError,
  AuthResponse,
  RefreshTokenRequest
} from '../types';

// Token management interface
interface TokenManager {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  setTokens(tokens: Pick<AuthResponse, 'accessToken' | 'refreshToken' | 'expiresAt'>): void;
  clearTokens(): void;
  isTokenExpired(): boolean;
  getExpiresAt(): number | null;
}

// Default token manager using localStorage
class LocalStorageTokenManager implements TokenManager {
  private readonly ACCESS_TOKEN_KEY = 'skillforge_access_token';
  private readonly REFRESH_TOKEN_KEY = 'skillforge_refresh_token';
  private readonly EXPIRES_AT_KEY = 'skillforge_expires_at';

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  setTokens(tokens: Pick<AuthResponse, 'accessToken' | 'refreshToken' | 'expiresAt'>): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refreshToken);
    localStorage.setItem(this.EXPIRES_AT_KEY, tokens.expiresAt.toString());
  }

  clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.EXPIRES_AT_KEY);
  }

  isTokenExpired(): boolean {
    const expiresAt = this.getExpiresAt();
    if (!expiresAt) return true;
    
    // Add 5 minute buffer to account for clock skew and network delay
    const bufferTime = 5 * 60 * 1000; // 5 minutes in milliseconds
    return Date.now() >= (expiresAt - bufferTime);
  }

  getExpiresAt(): number | null {
    const expiresAt = localStorage.getItem(this.EXPIRES_AT_KEY);
    return expiresAt ? parseInt(expiresAt, 10) : null;
  }
}

// API client configuration
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  tokenManager?: TokenManager;
  onAuthError?: () => void;
  enableCache?: boolean;
  cacheTTL?: number;
  enableRequestLogging?: boolean;
  enableResponseLogging?: boolean;
}

// Cache entry interface
interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
}

// Request cache
class RequestCache {
  private cache = new Map<string, CacheEntry>();

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.timestamp + entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set<T>(key: string, data: T, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  private createKey(url: string, params?: Record<string, any>): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${url}:${paramString}`;
  }
}

/**
 * Main API Client class
 */
export class ApiClient {
  private instance: AxiosInstance;
  private tokenManager: TokenManager;
  private cache: RequestCache;
  private refreshTokenPromise: Promise<AuthResponse> | null = null;
  private isRefreshing$ = new BehaviorSubject<boolean>(false);

  constructor(private config: ApiClientConfig) {
    this.tokenManager = config.tokenManager || new LocalStorageTokenManager();
    this.cache = new RequestCache();
    
    this.instance = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor for adding auth token
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add auth token if available and not already present
        if (!config.headers.Authorization) {
          const token = this.tokenManager.getAccessToken();
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }

        // Add request ID for tracing
        config.headers['X-Request-ID'] = this.generateRequestId();

        // Log request if enabled
        if (this.config.enableRequestLogging) {
          console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
            headers: config.headers,
            data: config.data,
          });
        }

        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for handling errors and token refresh
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response if enabled
        if (this.config.enableResponseLogging) {
          console.log(`[API Response] ${response.status} ${response.config.url}`, {
            data: response.data,
            headers: response.headers,
          });
        }

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config;

        // Handle different error types
        if (error.response) {
          const { status, data } = error.response;

          switch (status) {
            case 401:
              // Token expired or invalid
              if (originalRequest && !originalRequest.metadata?.retried) {
                try {
                  const newTokens = await this.refreshToken();
                  if (newTokens) {
                    originalRequest.headers = originalRequest.headers || {};
                    originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`;
                    originalRequest.metadata = { retried: true };
                    return this.instance.request(originalRequest);
                  }
                } catch (refreshError) {
                  this.handleAuthError();
                  throw new ApiAuthenticationError('Authentication failed');
                }
              } else {
                this.handleAuthError();
                throw new ApiAuthenticationError('Authentication failed');
              }
              break;

            case 403:
              throw new ApiAuthorizationError('Insufficient permissions');

            case 429:
              const retryAfter = error.response.headers['retry-after'];
              throw new ApiRateLimitError(
                'Rate limit exceeded',
                retryAfter ? parseInt(retryAfter, 10) * 1000 : undefined
              );

            default:
              throw new ApiNetworkError(
                (data as ApiError)?.message || error.message,
                status,
                error.response.statusText
              );
          }
        } else if (error.request) {
          // Network error
          throw new ApiNetworkError('Network error occurred');
        } else {
          // Other error
          throw new ApiNetworkError(error.message);
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Refresh access token
   */
  private async refreshToken(): Promise<AuthResponse | null> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise;
    }

    const refreshToken = this.tokenManager.getRefreshToken();
    if (!refreshToken) {
      this.handleAuthError();
      return null;
    }

    try {
      this.isRefreshing$.next(true);
      
      this.refreshTokenPromise = this.post<AuthResponse>('/auth/refresh', {
        refreshToken,
      }, { skipAuth: true });

      const response = await this.refreshTokenPromise;
      
      this.tokenManager.setTokens({
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        expiresAt: response.expiresAt,
      });

      return response;
    } catch (error) {
      console.error('[Token Refresh Error]', error);
      this.handleAuthError();
      return null;
    } finally {
      this.refreshTokenPromise = null;
      this.isRefreshing$.next(false);
    }
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(): void {
    this.tokenManager.clearTokens();
    this.cache.clear();
    this.config.onAuthError?.();
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Create cache key for request
   */
  private createCacheKey(url: string, params?: Record<string, any>): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${url}:${paramString}`;
  }

  /**
   * Generic request method with retry logic
   */
  private async request<T>(
    config: AxiosRequestConfig & { skipAuth?: boolean },
    requestConfig?: RequestConfig
  ): Promise<T> {
    const retries = requestConfig?.retries ?? this.config.retries ?? 3;
    const retryDelay = requestConfig?.retryDelay ?? this.config.retryDelay ?? 1000;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        // Check cache for GET requests
        if (config.method === 'GET' && (requestConfig?.cache ?? this.config.enableCache)) {
          const cacheKey = this.createCacheKey(config.url!, config.params);
          const cachedData = this.cache.get<T>(cacheKey);
          if (cachedData) {
            return cachedData;
          }
        }

        // Skip auth token for certain requests
        if (config.skipAuth) {
          delete config.headers?.Authorization;
        }

        const response = await this.instance.request<ApiResponse<T>>(config);
        const data = response.data.data;

        // Cache successful GET responses
        if (config.method === 'GET' && (requestConfig?.cache ?? this.config.enableCache)) {
          const cacheKey = this.createCacheKey(config.url!, config.params);
          const cacheTTL = requestConfig?.cacheTTL ?? this.config.cacheTTL ?? 5 * 60 * 1000; // 5 minutes
          this.cache.set(cacheKey, data, cacheTTL);
        }

        return data;
      } catch (error) {
        // Don't retry on auth errors or client errors (4xx)
        if (
          error instanceof ApiAuthenticationError ||
          error instanceof ApiAuthorizationError ||
          (error instanceof ApiNetworkError && error.status && error.status >= 400 && error.status < 500)
        ) {
          throw error;
        }

        // Retry on server errors or network issues
        if (attempt === retries) {
          throw error;
        }

        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
      }
    }

    throw new Error('Max retries exceeded');
  }

  /**
   * GET request
   */
  async get<T>(
    url: string,
    params?: Record<string, any>,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>({
      method: 'GET',
      url,
      params,
    }, config);
  }

  /**
   * POST request
   */
  async post<T>(
    url: string,
    data?: any,
    config?: RequestConfig & { skipAuth?: boolean }
  ): Promise<T> {
    return this.request<T>({
      method: 'POST',
      url,
      data,
      skipAuth: config?.skipAuth,
    }, config);
  }

  /**
   * PATCH request
   */
  async patch<T>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>({
      method: 'PATCH',
      url,
      data,
    }, config);
  }

  /**
   * PUT request
   */
  async put<T>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>({
      method: 'PUT',
      url,
      data,
    }, config);
  }

  /**
   * DELETE request
   */
  async delete<T>(
    url: string,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>({
      method: 'DELETE',
      url,
    }, config);
  }

  /**
   * Upload file
   */
  async upload<T>(
    url: string,
    file: File | FormData,
    config?: RequestConfig & {
      onUploadProgress?: (progressEvent: any) => void;
    }
  ): Promise<T> {
    const formData = file instanceof FormData ? file : new FormData();
    if (file instanceof File) {
      formData.append('file', file);
    }

    return this.request<T>({
      method: 'POST',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: config?.onUploadProgress,
    }, config);
  }

  /**
   * Set authentication tokens
   */
  setTokens(tokens: Pick<AuthResponse, 'accessToken' | 'refreshToken' | 'expiresAt'>): void {
    this.tokenManager.setTokens(tokens);
  }

  /**
   * Clear authentication tokens
   */
  clearTokens(): void {
    this.tokenManager.clearTokens();
    this.cache.clear();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.tokenManager.getAccessToken();
    return !!token && !this.tokenManager.isTokenExpired();
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | null {
    return this.tokenManager.getAccessToken();
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get instance for direct access
   */
  getInstance(): AxiosInstance {
    return this.instance;
  }
}

// Export types
export { TokenManager, LocalStorageTokenManager };