import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '@skillforge-ai/shared-state';
import { useUsersQuery, useProjectsQuery } from '@skillforge-ai/shared-state';
import { Button, Card, CardContent, CardHeader, CardTitle, StatsCard, FeatureCard } from '@skillforge-ai/ui-kit';
import { globalSignals } from '@skillforge-ai/shared-state';
import { useSignal } from '@preact/signals-react';

export const Dashboard: React.FC = () => {
  const { user, isAuthenticated, permissions } = useSelector((state: RootState) => state.auth);
  const loading = useSignal(globalSignals.ui.loading);

  // Fetch data using TanStack Query
  const { data: users, isLoading: usersLoading } = useUsersQuery();
  const { data: projects, isLoading: projectsLoading } = useProjectsQuery();

  const hasPermission = (permission: string) => permissions.includes(permission);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const roleBasedFeatures = [
    {
      title: 'Learning Path',
      description: 'Continue your personalized AI-powered learning journey',
      href: '/learning',
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      show: hasPermission('read:content'),
      color: 'bg-gradient-to-br from-primary-500 to-primary-600',
    },
    {
      title: 'Company Portal',
      description: 'Manage your team\'s learning initiatives and progress',
      href: '/company',
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
        </svg>
      ),
      show: hasPermission('read:company'),
      color: 'bg-gradient-to-br from-secondary-500 to-secondary-600',
    },
    {
      title: 'Admin Panel',
      description: 'Platform administration and user management',
      href: '/admin',
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
        </svg>
      ),
      show: hasPermission('read:admin'),
      color: 'bg-gradient-to-br from-warning-500 to-warning-600',
    },
  ];

  const statsData = [
    {
      title: 'Total Users',
      value: users?.length || 0,
      change: '+12%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
        </svg>
      ),
      show: hasPermission('read:users'),
    },
    {
      title: 'Active Projects',
      value: projects?.length || 0,
      change: '+8%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd" />
        </svg>
      ),
      show: hasPermission('read:projects'),
    },
    {
      title: 'Completion Rate',
      value: '94%',
      change: '+2%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ),
      show: true,
    },
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7v10c0 5.55 3.84 9.74 9 10.5C16.16 26.74 20 22.55 20 17V7l-8-5z"/>
              <path d="M8 11l2 2 4-4" stroke="currentColor" strokeWidth="2" fill="none"/>
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-4">
            Welcome to SkillForge AI
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 mb-8">
            Your AI-powered learning and development platform
          </p>
          <Button
            as={Link}
            to="/auth/login"
            variant="solid"
            color="primary"
            size="lg"
          >
            Get Started
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            {getGreeting()}, {user?.firstName}!
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 mt-1">
            Ready to continue your learning journey?
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            color="primary"
            leftIcon={
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
            }
            onClick={() => console.log('Open search')}
          >
            Quick Search
          </Button>
          
          {hasPermission('write:projects') && (
            <Button
              variant="solid"
              color="primary"
              leftIcon={
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
              }
              onClick={() => console.log('Create new project')}
            >
              New Project
            </Button>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statsData
          .filter(stat => stat.show)
          .map((stat, index) => (
            <StatsCard
              key={index}
              title={stat.title}
              value={stat.value}
              change={stat.change}
              changeType={stat.changeType}
              icon={stat.icon}
            />
          ))}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {roleBasedFeatures
          .filter(feature => feature.show)
          .map((feature, index) => (
            <FeatureCard
              key={index}
              title={feature.title}
              description={feature.description}
              href={feature.href}
              icon={feature.icon}
            />
          ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {hasPermission('read:content') && (
              <Button
                variant="ghost"
                fullWidth
                leftIcon={
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
                onClick={() => console.log('Continue learning')}
              >
                Continue Learning
              </Button>
            )}
            
            {hasPermission('write:projects') && (
              <Button
                variant="ghost"
                fullWidth
                leftIcon={
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                  </svg>
                }
                onClick={() => console.log('View team')}
              >
                View Team Progress
              </Button>
            )}
            
            <Button
              variant="ghost"
              fullWidth
              leftIcon={
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              }
              onClick={() => console.log('View help')}
            >
              Help & Support
            </Button>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">API Status</span>
              </div>
              <span className="text-sm font-medium text-success-600">Online</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Database</span>
              </div>
              <span className="text-sm font-medium text-success-600">Connected</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Cache</span>
              </div>
              <span className="text-sm font-medium text-warning-600">Optimizing</span>
            </div>
            
            <div className="pt-2 border-t border-neutral-200 dark:border-neutral-700">
              <p className="text-xs text-neutral-500 dark:text-neutral-500">
                Last updated: {new Date().toLocaleTimeString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};