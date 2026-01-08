'use client';

import { useQuery } from '@tanstack/react-query';
import { messagesAPI } from '@/lib/api';
import Link from 'next/link';
import { MessageCircle, ThumbsUp, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function CommentsPage() {
  const { data: comments, isLoading } = useQuery({
    queryKey: ['comments'],
    queryFn: async () => {
      // TODO: Create dedicated endpoint for comments
      // For now, mock data
      return {
        comments: [
          {
            id: 1,
            post_id: 1,
            post_content: 'Nouvelle routine anti-âge 💆‍♀️',
            author_username: 'marie_beauty',
            content: 'Quelle crème tu utilises ?',
            created_at: new Date().toISOString(),
            has_draft: false,
          },
        ],
      };
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
                Commentaires
              </h1>
              <p className="text-sm text-gray-500">
                Nouveaux commentaires Instagram
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
                href="/comments"
                className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium"
              >
                Commentaires
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow">
          <div className="divide-y divide-gray-200">
            {comments?.comments?.map((comment: any) => (
              <div key={comment.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                      <MessageCircle className="w-6 h-6 text-gray-600" />
                    </div>
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <span className="font-medium text-gray-900">
                          @{comment.author_username}
                        </span>
                        <span className="text-sm text-gray-500 ml-2">
                          sur "{comment.post_content}"
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(comment.created_at), {
                          addSuffix: true,
                          locale: fr,
                        })}
                      </span>
                    </div>

                    <p className="text-gray-700 mb-3">{comment.content}</p>

                    {comment.has_draft ? (
                      <button className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">
                        Voir brouillon IA
                      </button>
                    ) : (
                      <button className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm hover:bg-brand-700">
                        Générer réponse IA
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            <div className="p-12 text-center text-gray-500">
              <MessageCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>Simulation uniquement - intégration Meta Graph API requise</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
