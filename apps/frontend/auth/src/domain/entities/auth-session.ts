import { BaseEntity } from '@skillforge-ai/core';

export interface AuthSessionProps {
  userId: string;
  token: string;
  refreshToken: string;
  expiresAt: Date;
  deviceInfo?: string;
  ipAddress?: string;
}

export class AuthSession extends BaseEntity<string> {
  private _userId: string;
  private _token: string;
  private _refreshToken: string;
  private _expiresAt: Date;
  private _deviceInfo?: string;
  private _ipAddress?: string;

  constructor(id: string, props: AuthSessionProps, createdAt?: Date) {
    super(id, createdAt);
    
    this._userId = props.userId;
    this._token = props.token;
    this._refreshToken = props.refreshToken;
    this._expiresAt = props.expiresAt;
    this._deviceInfo = props.deviceInfo;
    this._ipAddress = props.ipAddress;
  }

  // Getters
  get userId(): string {
    return this._userId;
  }

  get token(): string {
    return this._token;
  }

  get refreshToken(): string {
    return this._refreshToken;
  }

  get expiresAt(): Date {
    return this._expiresAt;
  }

  get deviceInfo(): string | undefined {
    return this._deviceInfo;
  }

  get ipAddress(): string | undefined {
    return this._ipAddress;
  }

  // Business methods
  public isExpired(): boolean {
    return new Date() > this._expiresAt;
  }

  public isExpiringSoon(minutesBefore: number = 5): boolean {
    const expirationThreshold = new Date(this._expiresAt.getTime() - minutesBefore * 60 * 1000);
    return new Date() > expirationThreshold;
  }

  public updateTokens(token: string, refreshToken: string, expiresAt: Date): void {
    this._token = token;
    this._refreshToken = refreshToken;
    this._expiresAt = expiresAt;
    this.touch();
  }

  public toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      userId: this._userId,
      token: this._token,
      refreshToken: this._refreshToken,
      expiresAt: this._expiresAt,
      deviceInfo: this._deviceInfo,
      ipAddress: this._ipAddress,
    };
  }
}