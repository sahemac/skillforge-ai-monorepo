import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Simulation d'authentification avec redirection basée sur l'email
      if (email && password) {
        // Déterminer le type d'utilisateur et rediriger vers le bon dashboard
        let redirectPath = '/dashboard';

        if (email.includes('admin@skillforge.ai')) {
          redirectPath = '/admin/users';
        } else if (email.includes('company@techcorp.ai')) {
          redirectPath = '/company/dashboard';
        } else if (email.includes('student@skillforge.ai')) {
          redirectPath = '/learner/dashboard';
        } else {
          // Par défaut, utilisateur normal vers dashboard
          redirectPath = '/dashboard';
        }

        // Simulation d'un délai d'authentification avec redirection automatique
        setTimeout(() => {
          // Navigation avec React Router
          navigate(redirectPath);
        }, 1500);

      } else {
        setIsLoading(false);
        setError('Veuillez remplir tous les champs');
      }
    } catch (err) {
      setIsLoading(false);
      setError('Erreur de connexion. Vérifiez vos identifiants.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Connexion SkillForge AI
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Bienvenue sur votre plateforme d'apprentissage IA
          </p>

          {/* Instructions pour les comptes de test */}
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">Comptes de test disponibles:</h3>
            <div className="text-xs text-blue-700 space-y-1">
              <div><strong>Admin:</strong> admin@skillforge.ai / admin123</div>
              <div><strong>Entreprise:</strong> company@techcorp.ai / company123</div>
              <div><strong>Apprenant:</strong> student@skillforge.ai / student123</div>
            </div>
          </div>
        </div>

        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-gray-100">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Adresse Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                placeholder="votre.email@exemple.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                placeholder="Votre mot de passe"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                  Se souvenir de moi
                </label>
              </div>

              <div className="text-sm">
                <Link to="/auth/forgot-password" className="font-medium text-indigo-600 hover:text-indigo-500">
                  Mot de passe oublié ?
                </Link>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                    <span className="animate-pulse">Connexion et redirection...</span>
                  </div>
                ) : (
                  'Se Connecter'
                )}
              </button>
            </div>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                Pas encore de compte ?{' '}
                <Link to="/auth/register" className="font-medium text-indigo-600 hover:text-indigo-500">
                  Créer un compte
                </Link>
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};