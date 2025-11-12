import React, { useState } from 'react';
import { Project, ProjectStatus, ProjectType, ExperienceLevel } from '../domain/entities/project';

interface ProjectsListProps {
  projects?: Project[];
}

export const ProjectsList: React.FC<ProjectsListProps> = ({ projects = [] }) => {
  const [filter, setFilter] = useState<'all' | ProjectStatus>('all');
  const [sortBy, setSortBy] = useState<'date' | 'applications' | 'views'>('date');

  // Mock data for demonstration
  const mockProjects = projects.length > 0 ? projects : [
    new Project('1', {
      title: 'Senior React Developer',
      description: 'We are looking for an experienced React developer to join our frontend team.',
      companyId: 'company-1',
      type: ProjectType.FULL_TIME,
      status: ProjectStatus.PUBLISHED,
      experienceLevel: ExperienceLevel.SENIOR,
      location: 'San Francisco, CA',
      remote: true,
      salary: { min: 120000, max: 160000, currency: 'USD', period: 'yearly' },
      requirements: [
        { skill: 'React.js', level: 'advanced', required: true, yearsOfExperience: 5 },
        { skill: 'TypeScript', level: 'intermediate', required: true, yearsOfExperience: 3 },
        { skill: 'Next.js', level: 'intermediate', required: false, yearsOfExperience: 2 },
      ],
      benefits: ['Health Insurance', 'Remote Work', '401k', 'Flexible PTO'],
      applicationDeadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      startDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
      duration: 'Permanent',
      applicationsCount: 24,
      viewsCount: 156,
    }),
    new Project('2', {
      title: 'Backend Node.js Engineer',
      description: 'Join our backend team to build scalable microservices.',
      companyId: 'company-1',
      type: ProjectType.FULL_TIME,
      status: ProjectStatus.PUBLISHED,
      experienceLevel: ExperienceLevel.MIDDLE,
      location: 'Remote',
      remote: true,
      salary: { min: 90000, max: 130000, currency: 'USD', period: 'yearly' },
      requirements: [
        { skill: 'Node.js', level: 'advanced', required: true, yearsOfExperience: 4 },
        { skill: 'MongoDB', level: 'intermediate', required: true, yearsOfExperience: 2 },
      ],
      benefits: ['Health Insurance', 'Remote Work', 'Stock Options'],
      applicationDeadline: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000),
      startDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      duration: 'Permanent',
      applicationsCount: 18,
      viewsCount: 89,
    }),
    new Project('3', {
      title: 'DevOps Contractor',
      description: 'Short-term contract to migrate infrastructure to cloud.',
      companyId: 'company-1',
      type: ProjectType.CONTRACT,
      status: ProjectStatus.DRAFT,
      experienceLevel: ExperienceLevel.SENIOR,
      location: 'Remote',
      remote: true,
      salary: { min: 75, max: 95, currency: 'USD', period: 'hourly' },
      requirements: [
        { skill: 'Docker', level: 'advanced', required: true, yearsOfExperience: 3 },
        { skill: 'Kubernetes', level: 'advanced', required: true, yearsOfExperience: 2 },
      ],
      benefits: ['Flexible Schedule', 'High Hourly Rate'],
      applicationDeadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
      startDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      duration: '3 months',
      applicationsCount: 0,
      viewsCount: 12,
    }),
  ];

  const filteredProjects = mockProjects.filter(project => {
    if (filter === 'all') return true;
    return project.status === filter;
  });

  const sortedProjects = [...filteredProjects].sort((a, b) => {
    switch (sortBy) {
      case 'applications':
        return b.applicationsCount - a.applicationsCount;
      case 'views':
        return b.viewsCount - a.viewsCount;
      case 'date':
      default:
        return b.createdAt.getTime() - a.createdAt.getTime();
    }
  });

  const getStatusColor = (status: ProjectStatus): string => {
    switch (status) {
      case ProjectStatus.PUBLISHED:
        return 'bg-green-100 text-green-800';
      case ProjectStatus.DRAFT:
        return 'bg-gray-100 text-gray-800';
      case ProjectStatus.PAUSED:
        return 'bg-yellow-100 text-yellow-800';
      case ProjectStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800';
      case ProjectStatus.CANCELLED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: ProjectType): string => {
    switch (type) {
      case ProjectType.FULL_TIME:
        return '💼';
      case ProjectType.PART_TIME:
        return '⏰';
      case ProjectType.CONTRACT:
        return '📝';
      case ProjectType.FREELANCE:
        return '🎯';
      case ProjectType.INTERNSHIP:
        return '🎓';
      default:
        return '💼';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
              <p className="text-gray-600 mt-2">Manage and track your job postings</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2">
              <span>➕</span>
              <span>New Project</span>
            </button>
          </div>
        </div>

        {/* Filters and Sorting */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All ({mockProjects.length})
              </button>
              <button
                onClick={() => setFilter(ProjectStatus.PUBLISHED)}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === ProjectStatus.PUBLISHED ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Published ({mockProjects.filter(p => p.status === ProjectStatus.PUBLISHED).length})
              </button>
              <button
                onClick={() => setFilter(ProjectStatus.DRAFT)}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filter === ProjectStatus.DRAFT ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Draft ({mockProjects.filter(p => p.status === ProjectStatus.DRAFT).length})
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="date">Date Created</option>
                <option value="applications">Applications</option>
                <option value="views">Views</option>
              </select>
            </div>
          </div>
        </div>

        {/* Projects List */}
        <div className="space-y-4">
          {sortedProjects.map((project) => (
            <div key={project.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">{getTypeIcon(project.type)}</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
                        {project.title}
                      </h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                          {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {project.experienceLevel.charAt(0).toUpperCase() + project.experienceLevel.slice(1)} • {project.type.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-500">
                          {project.remote ? '🌍 Remote' : `📍 ${project.location}`}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    {project.salary && (
                      <div className="text-lg font-semibold text-gray-900">
                        {project.getSalaryRange()}
                      </div>
                    )}
                  </div>
                </div>

                <p className="text-gray-600 mb-4">{project.description}</p>

                {/* Skills */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-2">
                    {project.getRequiredSkills().slice(0, 5).map((skill) => (
                      <span key={skill} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {skill}
                      </span>
                    ))}
                    {project.getRequiredSkills().length > 5 && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        +{project.getRequiredSkills().length - 5} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Stats and Actions */}
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-1">
                      <span className="text-sm text-gray-500">📨</span>
                      <span className="text-sm text-gray-600">{project.applicationsCount} applications</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-sm text-gray-500">👁️</span>
                      <span className="text-sm text-gray-600">{project.viewsCount} views</span>
                    </div>
                    {project.applicationDeadline && (
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-500">⏰</span>
                        <span className="text-sm text-gray-600">Deadline: {project.applicationDeadline.toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {project.status === ProjectStatus.DRAFT && (
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Publish</button>
                    )}
                    {project.status === ProjectStatus.PUBLISHED && (
                      <button className="text-yellow-600 hover:text-yellow-800 text-sm font-medium">Pause</button>
                    )}
                    <button className="text-gray-600 hover:text-gray-800 text-sm font-medium">Edit</button>
                    <button className="text-red-600 hover:text-red-800 text-sm font-medium">Delete</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {sortedProjects.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects found</h3>
            <p className="text-gray-600 mb-6">
              {filter === 'all' ? "You haven't created any projects yet." : `No projects with status "${filter}" found.`}
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium">
              Create Your First Project
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
