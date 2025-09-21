import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './presentation/pages/login-page';
import { RegisterPage } from './presentation/pages/register-page';

export const AuthApp: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/*" element={<Navigate to="/auth/login" replace />} />
    </Routes>
  );
};

export default AuthApp;