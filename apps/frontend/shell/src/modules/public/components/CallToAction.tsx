import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@skillforge-ai/ui-kit';

export const CallToAction: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Prêt à transformer votre apprentissage ?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Rejoignez des centaines d'apprenants qui développent leurs compétences sur des projets réels
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link to="/register">
              <Button
                size="lg"
                className="w-full sm:w-auto bg-white text-blue-600 hover:bg-gray-100"
              >
                Créer un compte gratuit
              </Button>
            </Link>
            <Link to="/contact">
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-white text-white hover:bg-white hover:text-blue-600"
              >
                Nous contacter
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
