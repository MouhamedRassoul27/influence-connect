'use client';

import { useQuery } from '@tanstack/react-query';
import { evalAPI } from '@/lib/api';
import Link from 'next/link';
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  MessageCircle,
  CheckCircle,
} from 'lucide-react';

export default function DashboardPage() {
  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: async () => {
      const response = await evalAPI.getMetrics(7);
      return response.data;
    },
  });

  const stats = [
    {
      name: 'Taux d'approbation',
      value: `${((metrics?.approval_rate || 0) * 100).toFixed(1)}%`,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Taux d'édition',
      value: `${((metrics?.edit_rate || 0) * 100).toFixed(1)}%`,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Taux d'escalade',
      value: `${((metrics?.escalate_rate || 0) * 100).toFixed(1)}%`,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Confiance moyenne',
      value: `${((metrics?.avg_confidence || 0) * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-sm text-gray-500">
                Métriques qualité IA - 7 derniers jours
              </p>
            </div>
            <nav className="flex gap-4">
              <Link
                href="/inbox"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Inbox
              </Link>
              <Link
                href="/dashboard"
                className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium"
              >
                Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`${stat.bgColor} rounded-lg p-3`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    {stat.name}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Intents Distribution */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Top Intents (volume)
            </h2>
          </div>
          <div className="p-6">
            {metrics?.top_intents?.map((intent: any) => (
              <div key={intent.intent} className="mb-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">
                    {intent.intent}
                  </span>
                  <span className="text-sm text-gray-600">{intent.count}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-brand-600 h-2 rounded-full"
                    style={{
                      width: `${
                        (intent.count /
                          Math.max(
                            ...metrics.top_intents.map((i: any) => i.count)
                          )) *
                        100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Distribution des risques
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(metrics?.risk_distribution || {}).map(
                ([level, count]) => (
                  <div key={level} className="text-center">
                    <div
                      className={`text-3xl font-bold ${
                        level === 'critical'
                          ? 'text-red-600'
                          : level === 'high'
                          ? 'text-orange-600'
                          : level === 'medium'
                          ? 'text-yellow-600'
                          : 'text-green-600'
                      }`}
                    >
                      {count}
                    </div>
                    <div className="text-sm text-gray-600 capitalize">
                      {level}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
