import React from 'react';

export const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join SkillForge AI today
          </p>
        </div>
        
        <div className="bg-white py-8 px-6 shadow rounded-lg">
          <p className="text-center text-gray-600">
            Registration form coming soon...
          </p>
          <div className="mt-4 text-center">
            <a href="/auth/login" className="text-blue-600 hover:text-blue-500">
              Back to login
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};