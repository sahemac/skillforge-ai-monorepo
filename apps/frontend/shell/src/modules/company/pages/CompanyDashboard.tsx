import React, { useState, useEffect } from 'react';

interface DashboardStats {
  activeProjects: number;
  totalApplications: number;
  profileViews: number;
  matchedCandidates: number;
}

interface RecentActivity {
  id: string;
  type: 'application' | 'match' | 'view' | 'message';
  title: string;
  description: string;
  timestamp: Date;
}

export const CompanyDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    activeProjects: 0,
    totalApplications: 0,
    profileViews: 0,
    matchedCandidates: 0,
  });

  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // TODO: Replace with @skillforge-ai/api-client
        const response = await fetch('http://localhost:8001/api/dashboard/company');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        setStats(data.stats);
        setRecentActivity(data.recentActivity.map((activity: any) => ({
          ...activity,
          timestamp: new Date(activity.timestamp)
        })));
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        // Fallback to mock data
        setStats({
          activeProjects: 8,
          totalApplications: 124,
          profileViews: 2840,
          matchedCandidates: 32,
        });
        setRecentActivity([
          {
            id: '1',
            type: 'application',
            title: 'New Application (Mock)',
            description: 'Sarah Johnson applied for Senior React Developer',
            timestamp: new Date(Date.now() - 1000 * 60 * 30),
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatTimestamp = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return `${days}d ago`;
    }
  };

  const getActivityIcon = (type: RecentActivity['type']): string => {
    switch (type) {
      case 'application':
        return '📋';
      case 'match':
        return '✨';
      case 'view':
        return '👁️';
      case 'message':
        return '💬';
      default:
        return '📄';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Company Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome back! Here's what's happening with your talent acquisition.
          </p>
          {error && (
            <div className="mt-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
              ⚠️ Using mock data: {error}
            </div>
          )}
          {loading && (
            <div className="mt-4 p-3 bg-blue-100 border border-blue-400 text-blue-700 rounded">
              🔄 Loading dashboard data...
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Projects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.activeProjects}</p>
              </div>
              <div className="text-3xl">🚀</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-green-600">
                <span className="mr-1">↗</span>
                +12% from last month
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Applications</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalApplications}</p>
              </div>
              <div className="text-3xl">📨</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-green-600">
                <span className="mr-1">↗</span>
                +8% from last week
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Profile Views</p>
                <p className="text-2xl font-bold text-gray-900">{stats.profileViews}</p>
              </div>
              <div className="text-3xl">👁️</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-blue-600">
                <span className="mr-1">→</span>
                Same as last month
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">AI Matches</p>
                <p className="text-2xl font-bold text-gray-900">{stats.matchedCandidates}</p>
              </div>
              <div className="text-3xl">🎯</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-green-600">
                <span className="mr-1">↗</span>
                +24% from last month
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="text-2xl">{getActivityIcon(activity.type)}</div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                        <p className="text-sm text-gray-600">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">{formatTimestamp(activity.timestamp)}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    View all activity →
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
              </div>
              <div className="p-6 space-y-4">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2">
                  <span>➕</span>
                  <span>Post New Project</span>
                </button>

                <button className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2">
                  <span>🔍</span>
                  <span>Browse Candidates</span>
                </button>

                <button className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2">
                  <span>⚙️</span>
                  <span>Company Settings</span>
                </button>
              </div>
            </div>

            {/* Top Skills in Demand */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Top Skills in Demand</h2>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">React.js</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full w-4/5"></div>
                      </div>
                      <span className="text-xs text-gray-500">80%</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Node.js</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full w-3/5"></div>
                      </div>
                      <span className="text-xs text-gray-500">60%</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Python</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-600 h-2 rounded-full w-1/2"></div>
                      </div>
                      <span className="text-xs text-gray-500">50%</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">AWS</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full w-2/5"></div>
                      </div>
                      <span className="text-xs text-gray-500">40%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
