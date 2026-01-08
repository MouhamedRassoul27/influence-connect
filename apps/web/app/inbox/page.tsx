'use client';

import { useQuery } from '@tanstack/react-query';
import { messagesAPI } from '@/lib/api';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import { MessageCircle, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export default function InboxPage() {
  const { data: inbox, isLoading, error } = useQuery({
    queryKey: ['inbox'],
    queryFn: async () => {
      const response = await messagesAPI.getInbox();
      return response.data;
    },
    refetchInterval: 5000, // Poll every 5s
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Clock className="mx-auto h-12 w-12 text-gray-400 animate-spin" />
          <p className="mt-4 text-gray-600">Chargement de l'inbox...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <p className="mt-4 text-red-600">Erreur de chargement</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Influence Connect
              </h1>
              <p className="text-sm text-gray-500">
                Console HITL - L'Oréal Instagram
              </p>
            </div>
            <nav className="flex gap-4">
              <Link
                href="/inbox"
                className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium"
              >
                Inbox
              </Link>
              <Link
                href="/comments"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Commentaires
              </Link>
              <Link
                href="/influencers"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Influenceurs
              </Link>
              <Link
                href="/dashboard"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Inbox */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                Messages DM
              </h2>
              <span className="text-sm text-gray-500">
                {inbox?.threads?.length || 0} conversations
              </span>
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {inbox?.threads?.map((thread: any) => (
              <Link
                key={thread.id}
                href={`/thread/${thread.id}`}
                className="block hover:bg-gray-50 transition-colors"
              >
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center">
                        <MessageCircle className="w-6 h-6 text-brand-600" />
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          @{thread.participant_username}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDistanceToNow(
                            new Date(thread.last_message_at),
                            {
                              addSuffix: true,
                              locale: fr,
                            }
                          )}
                        </p>
                      </div>

                      <p className="mt-1 text-sm text-gray-600 truncate">
                        {thread.last_message_content}
                      </p>

                      <div className="mt-2 flex items-center gap-2">
                        {thread.status === 'open' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Ouvert
                          </span>
                        )}
                        {thread.pending_approval && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <Clock className="w-3 h-3 mr-1" />
                            En attente d'approbation
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}

            {(!inbox?.threads || inbox.threads.length === 0) && (
              <div className="p-12 text-center">
                <MessageCircle className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  Aucun message
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Les nouveaux messages DM apparaîtront ici.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
