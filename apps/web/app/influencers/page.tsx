'use client';

import { useQuery } from '@tanstack/react-query';
import { influencersAPI } from '@/lib/api';
import Link from 'next/link';
import { User, Instagram, Tag } from 'lucide-react';

export default function InfluencersPage() {
  const { data: influencers, isLoading } = useQuery({
    queryKey: ['influencers'],
    queryFn: async () => {
      const response = await influencersAPI.list('active');
      return response.data;
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Influenceurs
              </h1>
              <p className="text-sm text-gray-500">
                {influencers?.length || 0} ambassadeurs actifs
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
                href="/influencers"
                className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium"
              >
                Influenceurs
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="text-center py-12">Chargement...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {influencers?.map((influencer: any) => (
              <div
                key={influencer.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center">
                        <User className="w-8 h-8 text-brand-600" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {influencer.name}
                      </h3>
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Instagram className="w-4 h-4" />
                        <span>{influencer.instagram_handle}</span>
                      </div>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="mt-4">
                    <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                      <Tag className="w-3 h-3" />
                      <span>Tags</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {influencer.tags?.undertone && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {influencer.tags.undertone}
                        </span>
                      )}
                      {influencer.tags?.hair_type && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {influencer.tags.hair_type}
                        </span>
                      )}
                      {influencer.tags?.color_goal && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {influencer.tags.color_goal}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Promo code */}
                  {influencer.promo_code && (
                    <div className="mt-4 p-3 bg-brand-50 rounded-lg">
                      <p className="text-xs text-gray-600">Code promo</p>
                      <p className="text-sm font-mono font-bold text-brand-600">
                        {influencer.promo_code}
                      </p>
                    </div>
                  )}

                  {/* Commission */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-600">Commission</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {(influencer.commission_rate * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
