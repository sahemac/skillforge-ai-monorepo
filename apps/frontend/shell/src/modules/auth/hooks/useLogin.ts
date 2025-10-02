import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    role: string;
    first_name: string;
    last_name: string;
  };
}

export const useLogin = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Replace with real API call using @skillforge-ai/api-client
      // const response = await apiClient.auth.login(credentials);

      // Simulation pour migration progressive
      if (credentials.email && credentials.password) {
        // Déterminer la route de redirection basée sur le role
        let redirectPath = '/dashboard';

        if (credentials.email.includes('admin')) {
          redirectPath = '/admin/users';
        } else if (credentials.email.includes('company')) {
          redirectPath = '/company/dashboard';
        } else if (credentials.email.includes('student') || credentials.email.includes('learner')) {
          redirectPath = '/learner/dashboard';
        }

        // Simuler délai réseau
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Stocker token (temporaire - sera remplacé par AuthContext)
        localStorage.setItem('auth_token', 'mock_token');
        localStorage.setItem('user_role', credentials.email.includes('admin') ? 'admin' :
                                          credentials.email.includes('company') ? 'company' : 'learner');

        // Redirection
        navigate(redirectPath);

        return { success: true };
      } else {
        throw new Error('Email and password are required');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please check your credentials.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login,
    isLoading,
    error,
  };
};
