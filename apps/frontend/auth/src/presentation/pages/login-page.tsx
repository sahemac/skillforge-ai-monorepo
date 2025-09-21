import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginForm } from '../forms/login-form';
import { useLoginUseCase } from '../hooks/use-login-use-case';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useLoginUseCase();
  const [error, setError] = useState<string>('');

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      setError('');
      const result = await login(data);
      
      if (result.success) {
        // Navigate to dashboard or intended page
        navigate('/', { replace: true });
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Welcome back to SkillForge AI
          </p>
        </div>
        
        <div className="bg-white py-8 px-6 shadow rounded-lg">
          <LoginForm onSubmit={handleLogin} isLoading={isLoading} error={error} />
        </div>
      </div>
    </div>
  );
};