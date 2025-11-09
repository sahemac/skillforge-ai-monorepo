import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setAuthenticated, setUser, setPermissions } from '@skillforge-ai/shared-state';
import axios from 'axios';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Call real backend API directly with axios
      const { data } = await axios.post('http://localhost:8000/api/v1/auth/login', {
        email,
        password,
        remember_me: rememberMe,
      });

      // Extract user data from response (backend uses snake_case)
      const { user, access_token, refresh_token } = data;

      // 🔒 SÉCURITÉ: Bloquer admin sur frontend student/company
      if (user.role === 'admin') {
        setIsLoading(false);
        setError('Accès administrateur uniquement via api.emacsah.com');
        console.warn('Admin login attempt blocked on public frontend');
        return;
      }

      // Determine redirect path based on user role
      let redirectPath = '/learner/dashboard'; // Default

      switch (user.role) {
        case 'company_contact':
          redirectPath = '/company/dashboard';
          break;
        case 'user':
        case 'premium_user':
          redirectPath = '/learner/dashboard';
          break;
        default:
          redirectPath = '/learner/dashboard';
      }

      // Set default permissions based on role
      const permissions = user.role === 'admin'
        ? ['read:admin', 'write:admin', 'users:read', 'users:write', 'system:admin']
        : user.role === 'company_contact'
        ? ['read:company', 'write:company', 'projects:read', 'projects:write']
        : ['read:content', 'projects:read', 'profile:write'];

      // Update Redux state
      dispatch(setAuthenticated(true));
      dispatch(setUser({
        id: user.id,
        email: user.email,
        username: user.username || user.email.split('@')[0], // Use username from API or derive from email
        role: user.role,
        firstName: user.firstName,
        lastName: user.lastName,
        isActive: user.isActive ?? true, // Default to true if not provided
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
      }));
      dispatch(setPermissions(permissions));

      // Store tokens in localStorage
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);

      // Navigate to appropriate dashboard
      navigate(redirectPath);

    } catch (err: any) {
      setIsLoading(false);
      const errorMessage = err?.response?.data?.detail || err?.message || 'Erreur de connexion. Vérifiez vos identifiants.';
      setError(errorMessage);
      console.error('Login error:', err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left side - Branding avec gradient template */}
      <div className="bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white lg:w-1/2 p-12 flex flex-col justify-center items-center text-center">
        <div className="max-w-md">
          <div className="h-12 w-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center mx-auto mb-6">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-4">Bienvenue sur SkillForge AI</h1>
          <p className="text-indigo-100 mb-8">
            Connectez-vous pour accéder à votre espace d'apprentissage et suivre votre progression.
          </p>

          {/* Features cards */}
          <div className="bg-white bg-opacity-10 p-6 rounded-xl mb-6">
            <div className="flex items-center mb-4">
              <div className="bg-white bg-opacity-20 p-2 rounded-full mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>Évaluation IA instantanée</span>
            </div>
            <div className="flex items-center mb-4">
              <div className="bg-white bg-opacity-20 p-2 rounded-full mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>Portfolio automatique</span>
            </div>
            <div className="flex items-center">
              <div className="bg-white bg-opacity-20 p-2 rounded-full mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span>Suivi des compétences</span>
            </div>
          </div>

          {/* Test accounts */}
          <div className="bg-white bg-opacity-10 p-4 rounded-lg text-sm">
            <h3 className="font-semibold mb-2">Comptes de test:</h3>
            <div className="text-xs text-indigo-100 space-y-1">
              <div><strong>Admin:</strong> admin@skillforge.ai / admin123</div>
              <div><strong>Entreprise:</strong> company@techcorp.ai / company123</div>
              <div><strong>Apprenant:</strong> student@skillforge.ai / student123</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="lg:w-1/2 p-8 lg:p-16 flex flex-col justify-center bg-gray-50">
        <div className="max-w-md mx-auto w-full">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Connectez-vous</h2>
          <p className="text-gray-600 mb-8">Entrez vos identifiants pour accéder à votre compte.</p>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Adresse email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="email@exemple.com"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Mot de passe
                </label>
                <Link to="/auth/forgot-password" className="text-sm text-indigo-600 hover:text-indigo-500">
                  Mot de passe oublié ?
                </Link>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Votre mot de passe"
              />
            </div>

            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                Se souvenir de moi
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                  <span>Connexion en cours...</span>
                </div>
              ) : (
                'Se connecter'
              )}
            </button>
          </form>

          {/* Social Login */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">ou</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                <span className="ml-2">GitHub</span>
              </button>
              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" />
                </svg>
                <span className="ml-2">Google</span>
              </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Pas encore de compte ?{' '}
              <Link to="/auth/register" className="font-medium text-indigo-600 hover:text-indigo-500">
                S'inscrire
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};