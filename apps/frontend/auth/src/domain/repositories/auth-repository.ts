import { User, Email } from '@skillforge-ai/core';
import { AuthSession } from '../entities/auth-session';
import { Password } from '../value-objects/password';

export interface LoginCredentials {
  email: Email;
  password: Password;
}

export interface RegisterData {
  email: Email;
  password: Password;
  firstName: string;
  lastName: string;
  role: 'learner' | 'company';
}

export interface AuthResult {
  user: User;
  session: AuthSession;
}

export interface IAuthRepository {
  login(credentials: LoginCredentials): Promise<AuthResult>;
  register(data: RegisterData): Promise<AuthResult>;
  logout(sessionId: string): Promise<void>;
  refreshToken(refreshToken: string): Promise<AuthSession>;
  verifyEmail(token: string): Promise<void>;
  requestPasswordReset(email: Email): Promise<void>;
  resetPassword(token: string, newPassword: Password): Promise<void>;
  getCurrentUser(): Promise<User | null>;
}