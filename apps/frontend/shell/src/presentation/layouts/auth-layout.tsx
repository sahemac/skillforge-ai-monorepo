/**
 * Authentication Layout
 * Dedicated layout for authentication-related pages
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import { Card, CardContent } from '@skillforge-ai/ui-kit';
import { useTheme } from '@skillforge-ai/ui-kit';

interface AuthLayoutProps {
  children?: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-neutral-900 dark:to-neutral-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Theme Toggle */}
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-white dark:bg-neutral-800 shadow-sm hover:shadow-md transition-all duration-200"
            aria-label="Toggle theme"
          >
            {isDark ? (
              <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-neutral-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>

        {/* Main Content Card */}
        <Card variant="elevated" className="overflow-hidden">
          <CardContent className="p-8">
            {/* Logo Section */}
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mb-4">
                <svg 
                  className="w-8 h-8 text-white" 
                  fill="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2L2 7v10c0 5.55 3.84 9.74 9 10.5C16.16 26.74 20 22.55 20 17V7l-8-5z"/>
                  <path d="M8 11l2 2 4-4" stroke="currentColor" strokeWidth="2" fill="none"/>
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">
                SkillForge AI
              </h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-2">
                Enterprise Learning Platform
              </p>
            </div>

            {/* Content */}
            {children || <Outlet />}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-neutral-600 dark:text-neutral-400">
          <p>
            © 2025 SkillForge AI. All rights reserved.
          </p>
          <div className="flex justify-center space-x-4 mt-2">
            <a href="/terms" className="hover:text-primary-600 transition-colors">
              Terms
            </a>
            <a href="/privacy" className="hover:text-primary-600 transition-colors">
              Privacy
            </a>
            <a href="/support" className="hover:text-primary-600 transition-colors">
              Support
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};