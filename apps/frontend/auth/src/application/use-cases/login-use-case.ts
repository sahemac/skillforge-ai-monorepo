import { Email } from '@skillforge-ai/core';
import { IAuthRepository, LoginCredentials, AuthResult } from '../../domain/repositories/auth-repository';
import { Password } from '../../domain/value-objects/password';

export interface LoginUseCaseInput {
  email: string;
  password: string;
}

export interface LoginUseCaseOutput {
  success: boolean;
  result?: AuthResult;
  error?: string;
}

export class LoginUseCase {
  constructor(private authRepository: IAuthRepository) {}

  async execute(input: LoginUseCaseInput): Promise<LoginUseCaseOutput> {
    try {
      // Validate input
      const email = new Email(input.email);
      const password = new Password(input.password);

      const credentials: LoginCredentials = {
        email,
        password,
      };

      // Execute login
      const result = await this.authRepository.login(credentials);

      return {
        success: true,
        result,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed',
      };
    }
  }
}