import { User, UserRole, UserStatus, Email } from '@skillforge-ai/core';
import { IAuthRepository, LoginCredentials, RegisterData, AuthResult } from '../../domain/repositories/auth-repository';
import { AuthSession } from '../../domain/entities/auth-session';
import { Password } from '../../domain/value-objects/password';
import { AuthApiClient } from '../api/auth-api-client';

export class AuthRepositoryImpl implements IAuthRepository {
  constructor(private apiClient: AuthApiClient) {}

  async login(credentials: LoginCredentials): Promise<AuthResult> {
    const response = await this.apiClient.login({
      email: credentials.email.getValue(),
      password: credentials.password.getValue(),
    });

    const user = this.mapToUserEntity(response.user);
    const session = this.mapToSessionEntity(response.session);

    return { user, session };
  }

  async register(data: RegisterData): Promise<AuthResult> {
    const response = await this.apiClient.register({
      email: data.email.getValue(),
      password: data.password.getValue(),
      firstName: data.firstName,
      lastName: data.lastName,
      role: data.role,
    });

    const user = this.mapToUserEntity(response.user);
    const session = this.mapToSessionEntity(response.session);

    return { user, session };
  }

  async logout(sessionId: string): Promise<void> {
    await this.apiClient.logout(sessionId);
  }

  async refreshToken(refreshToken: string): Promise<AuthSession> {
    const response = await this.apiClient.refreshToken(refreshToken);
    return this.mapToSessionEntity(response);
  }

  async verifyEmail(token: string): Promise<void> {
    await this.apiClient.verifyEmail(token);
  }

  async requestPasswordReset(email: Email): Promise<void> {
    await this.apiClient.requestPasswordReset(email.getValue());
  }

  async resetPassword(token: string, newPassword: Password): Promise<void> {
    await this.apiClient.resetPassword(token, newPassword.getValue());
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await this.apiClient.getCurrentUser();
      return response ? this.mapToUserEntity(response) : null;
    } catch (error) {
      return null;
    }
  }

  private mapToUserEntity(userData: any): User {
    const email = new Email(userData.email);
    
    return new User(
      userData.id,
      {
        email,
        firstName: userData.firstName,
        lastName: userData.lastName,
        role: userData.role as UserRole,
        status: userData.status as UserStatus,
        profilePicture: userData.profilePicture,
        lastLoginAt: userData.lastLoginAt ? new Date(userData.lastLoginAt) : undefined,
      },
      userData.createdAt ? new Date(userData.createdAt) : undefined
    );
  }

  private mapToSessionEntity(sessionData: any): AuthSession {
    return new AuthSession(
      sessionData.id,
      {
        userId: sessionData.userId,
        token: sessionData.token,
        refreshToken: sessionData.refreshToken,
        expiresAt: new Date(sessionData.expiresAt),
        deviceInfo: sessionData.deviceInfo,
        ipAddress: sessionData.ipAddress,
      },
      sessionData.createdAt ? new Date(sessionData.createdAt) : undefined
    );
  }
}