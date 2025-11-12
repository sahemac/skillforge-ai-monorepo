import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: 'learner' | 'company';
}

interface RegisterResponse {
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  };
  message: string;
}

export const useRegister = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (data: RegisterData) => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Replace with real API call using @skillforge-ai/api-client
      // const response = await apiClient.auth.register({
      //   email: data.email,
      //   username: data.email.split('@')[0],
      //   password: data.password,
      //   confirm_password: data.password,
      //   first_name: data.firstName,
      //   last_name: data.lastName,
      //   terms_accepted: true,
      //   privacy_policy_accepted: true,
      // });

      // Validation basique
      if (!data.email || !data.password || !data.firstName || !data.lastName) {
        throw new Error('All fields are required');
      }

      if (data.password.length < 8) {
        throw new Error('Password must be at least 8 characters');
      }

      // Simuler délai réseau
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simuler succès
      console.log('Registration successful:', data);

      // Rediriger vers login avec message de succès
      navigate('/auth/login', {
        state: {
          message: 'Registration successful! Please check your email to verify your account.',
          email: data.email,
        },
      });

      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    register,
    isLoading,
    error,
  };
};
