import { Email, UserRole } from '@skillforge-ai/core';
import { IAuthRepository, RegisterData, AuthResult } from '../../domain/repositories/auth-repository';
import { Password } from '../../domain/value-objects/password';

export interface RegisterUseCaseInput {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  role: 'learner' | 'company';
}

export interface RegisterUseCaseOutput {
  success: boolean;
  result?: AuthResult;
  error?: string;
}

export class RegisterUseCase {
  constructor(private authRepository: IAuthRepository) {}

  async execute(input: RegisterUseCaseInput): Promise<RegisterUseCaseOutput> {
    try {
      // Validate password confirmation
      if (input.password !== input.confirmPassword) {
        return {
          success: false,
          error: 'Passwords do not match',
        };
      }

      // Validate and create value objects
      const email = new Email(input.email);
      const password = new Password(input.password);

      // Validate names
      if (!input.firstName.trim() || !input.lastName.trim()) {
        return {
          success: false,
          error: 'First name and last name are required',
        };
      }

      const registerData: RegisterData = {
        email,
        password,
        firstName: input.firstName.trim(),
        lastName: input.lastName.trim(),
        role: input.role,
      };

      // Execute registration
      const result = await this.authRepository.register(registerData);

      return {
        success: true,
        result,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      };
    }
  }
}