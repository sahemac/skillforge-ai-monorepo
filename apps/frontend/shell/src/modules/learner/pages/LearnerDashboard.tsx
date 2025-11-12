import React, { useState, useEffect } from 'react';

interface LearningStats {
  coursesCompleted: number;
  skillsLearned: number;
  studyStreak: number;
  certificatesEarned: number;
}

interface Course {
  id: string;
  title: string;
  progress: number;
  instructor: string;
  duration: string;
  category: string;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt: Date;
}

export const LearnerDashboard: React.FC = () => {
  const [stats, setStats] = useState<LearningStats>({
    coursesCompleted: 0,
    skillsLearned: 0,
    studyStreak: 0,
    certificatesEarned: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // TODO: Replace with @skillforge-ai/api-client
        const response = await fetch('http://localhost:8001/api/dashboard/learner');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        setStats(data.stats);
      } catch (err) {
        console.error('Failed to fetch learner dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        // Fallback to mock data
        setStats({
          coursesCompleted: 12,
          skillsLearned: 28,
          studyStreak: 15,
          certificatesEarned: 5,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const [currentCourses] = useState<Course[]>([
    {
      id: '1',
      title: 'Advanced React & TypeScript',
      progress: 78,
      instructor: 'Sarah Mitchell',
      duration: '6 semaines',
      category: 'Développement Frontend',
    },
    {
      id: '2',
      title: 'Intelligence Artificielle avec Python',
      progress: 45,
      instructor: 'Dr. Ahmed Hassan',
      duration: '8 semaines',
      category: 'IA & Machine Learning',
    },
    {
      id: '3',
      title: 'Design System & UI/UX',
      progress: 92,
      instructor: 'Luna Rodriguez',
      duration: '4 semaines',
      category: 'Design',
    },
  ]);

  const [recentAchievements] = useState<Achievement[]>([
    {
      id: '1',
      title: 'React Master',
      description: 'Completed 5 React courses with excellence',
      icon: '🚀',
      unlockedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2),
    },
    {
      id: '2',
      title: 'Study Streak Champion',
      description: 'Maintained a 15-day study streak',
      icon: '🔥',
      unlockedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1),
    },
  ]);

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Mon Tableau de Bord</h1>
          <p className="text-gray-600 mt-2">
            Bonjour ! Continuez votre parcours d'apprentissage avec SkillForge AI.
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
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Cours Terminés</p>
                <p className="text-2xl font-bold text-gray-900">{stats.coursesCompleted}</p>
              </div>
              <div className="text-3xl">📚</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-green-600">
                <span className="mr-1">↗</span>
                +3 ce mois-ci
              </span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Compétences Acquises</p>
                <p className="text-2xl font-bold text-gray-900">{stats.skillsLearned}</p>
              </div>
              <div className="text-3xl">🎯</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-green-600">
                <span className="mr-1">↗</span>
                +5 cette semaine
              </span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Série d'Étude</p>
                <p className="text-2xl font-bold text-gray-900">{stats.studyStreak} jours</p>
              </div>
              <div className="text-3xl">🔥</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-orange-600">
                <span className="mr-1">🎯</span>
                Record personnel !
              </span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Certificats</p>
                <p className="text-2xl font-bold text-gray-900">{stats.certificatesEarned}</p>
              </div>
              <div className="text-3xl">🏆</div>
            </div>
            <div className="mt-4">
              <span className="inline-flex items-center text-sm text-purple-600">
                <span className="mr-1">✨</span>
                +2 ce trimestre
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Current Courses */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Cours En Cours</h2>
              </div>
              <div className="p-6">
                <div className="space-y-6">
                  {currentCourses.map((course) => (
                    <div key={course.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">{course.title}</h3>
                          <p className="text-sm text-gray-600">Par {course.instructor}</p>
                        </div>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {course.category}
                        </span>
                      </div>

                      <div className="mb-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-gray-700">Progression</span>
                          <span className="text-sm font-medium text-gray-900">{course.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${course.progress}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">⏱️ {course.duration}</span>
                        <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                          Continuer
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Achievements & Actions */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Actions Rapides</h2>
              </div>
              <div className="p-6 space-y-4">
                <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2 transition-all">
                  <span>🔍</span>
                  <span>Parcourir les Cours</span>
                </button>

                <button className="w-full border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-gray-700 px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2 transition-all">
                  <span>📊</span>
                  <span>Évaluation de Compétences</span>
                </button>

                <button className="w-full border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 text-gray-700 px-4 py-3 rounded-lg font-medium flex items-center justify-center space-x-2 transition-all">
                  <span>🎯</span>
                  <span>Définir Objectifs</span>
                </button>
              </div>
            </div>

            {/* Recent Achievements */}
            <div className="bg-white rounded-xl shadow-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Succès Récents</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {recentAchievements.map((achievement) => (
                    <div key={achievement.id} className="flex items-start space-x-3 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                      <div className="text-2xl">{achievement.icon}</div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{achievement.title}</p>
                        <p className="text-xs text-gray-600">{achievement.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Débloqué le {formatDate(achievement.unlockedAt)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Voir tous les succès →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
