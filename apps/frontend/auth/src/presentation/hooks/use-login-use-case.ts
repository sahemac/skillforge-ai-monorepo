import { useState } from 'react';
import { LoginUseCase, LoginUseCaseInput, LoginUseCaseOutput } from '../../application/use-cases/login-use-case';
import { AuthRepositoryImpl } from '../../infrastructure/adapters/auth-repository-impl';
import { AuthApiClient } from '../../infrastructure/api/auth-api-client';

// Dependency injection container - in a real app, this would be properly injected
const createLoginUseCase = () => {
  const apiClient = new AuthApiClient();
  const authRepository = new AuthRepositoryImpl(apiClient);
  return new LoginUseCase(authRepository);
};

export const useLoginUseCase = () => {
  const [isLoading, setIsLoading] = useState(false);
  const loginUseCase = createLoginUseCase();

  const login = async (input: LoginUseCaseInput): Promise<LoginUseCaseOutput> => {
    setIsLoading(true);
    try {
      const result = await loginUseCase.execute(input);
      
      // If login successful, store auth data
      if (result.success && result.result) {
        localStorage.setItem('auth_token', result.result.session.token);
        localStorage.setItem('user', JSON.stringify(result.result.user.toJSON()));
        
        // Trigger a custom event for the shell app to update its state
        window.dispatchEvent(new CustomEvent('auth:login', {
          detail: {
            user: result.result.user.toJSON(),
            session: result.result.session.toJSON(),
          }
        }));
      }
      
      return result;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login,
    isLoading,
  };
};