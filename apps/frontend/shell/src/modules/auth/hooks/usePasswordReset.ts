import { useState } from 'react';

interface PasswordResetRequestData {
  email: string;
}

interface PasswordResetConfirmData {
  token: string;
  password: string;
  confirmPassword: string;
}

export const usePasswordReset = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const requestPasswordReset = async (data: PasswordResetRequestData) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // TODO: Replace with real API call using @skillforge-ai/api-client
      // const response = await apiClient.auth.requestPasswordReset(data.email);

      if (!data.email) {
        throw new Error('Email is required');
      }

      // Simuler délai réseau
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log('Password reset email sent to:', data.email);
      setSuccess(true);

      return { success: true, message: 'Password reset email sent successfully' };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send password reset email';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const confirmPasswordReset = async (data: PasswordResetConfirmData) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // TODO: Replace with real API call using @skillforge-ai/api-client
      // const response = await apiClient.auth.confirmPasswordReset({
      //   token: data.token,
      //   new_password: data.password,
      //   confirm_password: data.confirmPassword,
      // });

      if (data.password !== data.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      if (data.password.length < 8) {
        throw new Error('Password must be at least 8 characters');
      }

      // Simuler délai réseau
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log('Password reset confirmed for token:', data.token);
      setSuccess(true);

      return { success: true, message: 'Password reset successfully' };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset password';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    requestPasswordReset,
    confirmPasswordReset,
    isLoading,
    error,
    success,
  };
};
