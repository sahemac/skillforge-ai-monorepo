import React, { useState } from 'react';

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: 'learner' | 'company' | 'admin';
  status: 'active' | 'suspended' | 'pending';
  registeredAt: Date;
}

export const AdminDashboard: React.FC = () => {
  const [users] = useState<User[]>([
    {
      id: '1',
      firstName: 'Sarah',
      lastName: 'Johnson',
      email: 'sarah.johnson@example.com',
      role: 'learner',
      status: 'active',
      registeredAt: new Date('2024-01-15'),
    },
    {
      id: '2',
      firstName: 'Tech',
      lastName: 'Corp',
      email: 'contact@techcorp.com',
      role: 'company',
      status: 'active',
      registeredAt: new Date('2024-02-20'),
    },
    {
      id: '3',
      firstName: 'Ahmed',
      lastName: 'Hassan',
      email: 'ahmed.hassan@example.com',
      role: 'learner',
      status: 'active',
      registeredAt: new Date('2024-03-10'),
    },
    {
      id: '4',
      firstName: 'Innovation',
      lastName: 'Labs',
      email: 'hr@innovationlabs.com',
      role: 'company',
      status: 'pending',
      registeredAt: new Date('2024-09-01'),
    },
    {
      id: '5',
      firstName: 'Luna',
      lastName: 'Rodriguez',
      email: 'luna.r@example.com',
      role: 'learner',
      status: 'suspended',
      registeredAt: new Date('2024-05-05'),
    },
  ]);

  const [filter, setFilter] = useState<'all' | 'learner' | 'company' | 'admin'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'suspended' | 'pending'>('all');

  const filteredUsers = users.filter(user => {
    if (filter !== 'all' && user.role !== filter) return false;
    if (statusFilter !== 'all' && user.status !== statusFilter) return false;
    return true;
  });

  const getStatusColor = (status: User['status']): string => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleIcon = (role: User['role']): string => {
    switch (role) {
      case 'learner':
        return '🎓';
      case 'company':
        return '🏢';
      case 'admin':
        return '👨‍💼';
      default:
        return '👤';
    }
  };

  const stats = {
    totalUsers: users.length,
    learners: users.filter(u => u.role === 'learner').length,
    companies: users.filter(u => u.role === 'company').length,
    pending: users.filter(u => u.status === 'pending').length,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage users and platform settings</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
              </div>
              <div className="text-3xl">👥</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Learners</p>
                <p className="text-2xl font-bold text-gray-900">{stats.learners}</p>
              </div>
              <div className="text-3xl">🎓</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Companies</p>
                <p className="text-2xl font-bold text-gray-900">{stats.companies}</p>
              </div>
              <div className="text-3xl">🏢</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              </div>
              <div className="text-3xl">⏳</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700 self-center mr-2">Role:</span>
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter('learner')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === 'learner' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Learners
              </button>
              <button
                onClick={() => setFilter('company')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === 'company' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Companies
              </button>
            </div>

            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700 self-center mr-2">Status:</span>
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('active')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusFilter === 'active' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setStatusFilter('pending')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusFilter === 'pending' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Pending
              </button>
              <button
                onClick={() => setStatusFilter('suspended')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusFilter === 'suspended' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Suspended
              </button>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Users ({filteredUsers.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Registered
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-2xl mr-3">{getRoleIcon(user.role)}</div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {user.firstName} {user.lastName}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-700 capitalize">{user.role}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(user.status)}`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.registeredAt.toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900 mr-4">Edit</button>
                      {user.status === 'active' ? (
                        <button className="text-yellow-600 hover:text-yellow-900 mr-4">Suspend</button>
                      ) : user.status === 'suspended' ? (
                        <button className="text-green-600 hover:text-green-900 mr-4">Activate</button>
                      ) : (
                        <button className="text-green-600 hover:text-green-900 mr-4">Approve</button>
                      )}
                      <button className="text-red-600 hover:text-red-900">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
