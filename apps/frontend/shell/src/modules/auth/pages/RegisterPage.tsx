import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterForm } from '../forms/register-form';
import { useRegisterUseCase } from '../hooks/use-register-use-case';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useRegisterUseCase();
  const [error, setError] = useState<string>('');

  const handleRegister = async (data: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    role: 'learner' | 'company'
  }) => {
    try {
      setError('');
      const result = await register(data);

      if (result.success) {
        // Navigate to dashboard or intended page based on role
        const dashboardPath = data.role === 'company' ? '/company' : '/learner';
        navigate(dashboardPath, { replace: true });
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (err) {
      setError('An unexpected error occurred during registration');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join SkillForge AI today and unlock your potential
          </p>
        </div>

        <div className="bg-white py-8 px-6 shadow-lg rounded-lg">
          <RegisterForm
            onSubmit={handleRegister}
            isLoading={isLoading}
            error={error}
          />
        </div>
      </div>
    </div>
  );
};