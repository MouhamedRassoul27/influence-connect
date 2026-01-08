'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messagesAPI, type ApprovalAction } from '@/lib/api';
import { useParams } from 'next/navigation';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  AlertTriangle,
  CheckCircle,
  Edit3,
  Send,
  ShieldAlert,
  Sparkles,
  User,
} from 'lucide-react';
import { useState } from 'react';

export default function ThreadPage() {
  const params = useParams();
  const threadId = Number(params.id);
  const queryClient = useQueryClient();
  const [editedText, setEditedText] = useState('');
  const [editingDraftId, setEditingDraftId] = useState<number | null>(null);

  const { data: thread, isLoading } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: async () => {
      const response = await messagesAPI.getThread(threadId);
      return response.data;
    },
  });

  const approveMutation = useMutation({
    mutationFn: async ({
      messageId,
      draftId,
      action,
    }: {
      messageId: number;
      draftId: number;
      action: ApprovalAction;
    }) => {
      await messagesAPI.approve(messageId, draftId, action);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thread', threadId] });
      setEditingDraftId(null);
      setEditedText('');
    },
  });

  const handleApprove = (messageId: number, draftId: number) => {
    approveMutation.mutate({
      messageId,
      draftId,
      action: { action: 'approve' },
    });
  };

  const handleEdit = (draftId: number, currentText: string) => {
    setEditingDraftId(draftId);
    setEditedText(currentText);
  };

  const handleSaveEdit = (messageId: number, draftId: number) => {
    approveMutation.mutate({
      messageId,
      draftId,
      action: { action: 'edit', edited_text: editedText },
    });
  };

  const handleEscalate = (messageId: number, draftId: number) => {
    const reason = prompt('Raison de l'escalade :');
    if (reason) {
      approveMutation.mutate({
        messageId,
        draftId,
        action: { action: 'escalate', escalation_reason: reason },
      });
    }
  };

  if (isLoading) {
    return <div className="p-8">Chargement...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <a
              href="/inbox"
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              ← Retour
            </a>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Conversation avec @{thread?.thread?.participant_username}
              </h1>
              <p className="text-sm text-gray-500">
                {thread?.thread?.status === 'open' ? 'Ouverte' : 'Fermée'}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Thread */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {thread?.messages?.map((msg: any) => (
            <div key={msg.id}>
              {/* User message */}
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <User className="w-4 h-4 text-gray-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-white rounded-lg shadow-sm p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        @{msg.sender_username}
                      </span>
                      <span className="text-xs text-gray-500">
                        {format(new Date(msg.created_at), 'PPp', { locale: fr })}
                      </span>
                    </div>
                    <p className="text-gray-700">{msg.content}</p>
                  </div>
                </div>
              </div>

              {/* AI Draft */}
              {msg.draft && (
                <div className="ml-11 mt-4">
                  <div className="bg-brand-50 border-2 border-brand-200 rounded-lg p-4">
                    {/* Classification */}
                    <div className="mb-4 pb-4 border-b border-brand-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="w-4 h-4 text-brand-600" />
                        <span className="text-sm font-semibold text-brand-900">
                          Classification IA
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-600">Intent:</span>{' '}
                          <span className="font-medium">
                            {msg.classification?.intent}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Confiance:</span>{' '}
                          <span className="font-medium">
                            {(msg.classification?.intent_confidence * 100).toFixed(
                              0
                            )}
                            %
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Risk Level:</span>{' '}
                          <span
                            className={`font-medium ${
                              msg.classification?.risk_level === 'critical'
                                ? 'text-red-600'
                                : msg.classification?.risk_level === 'high'
                                ? 'text-orange-600'
                                : 'text-green-600'
                            }`}
                          >
                            {msg.classification?.risk_level}
                          </span>
                        </div>
                        {msg.classification?.risk_flags?.length > 0 && (
                          <div>
                            <span className="text-gray-600">Flags:</span>{' '}
                            <span className="font-medium text-red-600">
                              {msg.classification.risk_flags.join(', ')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Draft reply */}
                    <div className="mb-4">
                      <label className="text-sm font-semibold text-brand-900 mb-2 block">
                        Réponse proposée
                      </label>
                      {editingDraftId === msg.draft.id ? (
                        <textarea
                          value={editedText}
                          onChange={(e) => setEditedText(e.target.value)}
                          className="w-full p-3 border border-brand-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                          rows={4}
                        />
                      ) : (
                        <p className="text-gray-700 bg-white p-3 rounded border border-brand-200">
                          {msg.draft.reply_text}
                        </p>
                      )}
                    </div>

                    {/* Verification */}
                    {msg.verification && (
                      <div className="mb-4 p-3 bg-white rounded border border-brand-200">
                        <div className="flex items-center gap-2 mb-2">
                          {msg.verification.verdict === 'PASS' ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-orange-600" />
                          )}
                          <span className="text-sm font-semibold">
                            Vérification: {msg.verification.verdict}
                          </span>
                        </div>
                        {msg.verification.issues?.length > 0 && (
                          <ul className="text-xs space-y-1">
                            {msg.verification.issues.map(
                              (issue: any, idx: number) => (
                                <li key={idx} className="text-red-600">
                                  • {issue.description}
                                </li>
                              )
                            )}
                          </ul>
                        )}
                      </div>
                    )}

                    {/* Actions */}
                    {msg.requires_hitl && !msg.approval && (
                      <div className="flex gap-2">
                        {editingDraftId === msg.draft.id ? (
                          <>
                            <button
                              onClick={() => handleSaveEdit(msg.id, msg.draft.id)}
                              className="flex-1 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 flex items-center justify-center gap-2"
                            >
                              <Send className="w-4 h-4" />
                              Envoyer (édité)
                            </button>
                            <button
                              onClick={() => setEditingDraftId(null)}
                              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                            >
                              Annuler
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => handleApprove(msg.id, msg.draft.id)}
                              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
                            >
                              <CheckCircle className="w-4 h-4" />
                              Approuver
                            </button>
                            <button
                              onClick={() =>
                                handleEdit(msg.draft.id, msg.draft.reply_text)
                              }
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                            >
                              <Edit3 className="w-4 h-4" />
                              Éditer
                            </button>
                            <button
                              onClick={() => handleEscalate(msg.id, msg.draft.id)}
                              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center justify-center gap-2"
                            >
                              <ShieldAlert className="w-4 h-4" />
                              Escalader
                            </button>
                          </>
                        )}
                      </div>
                    )}

                    {/* Approval status */}
                    {msg.approval && (
                      <div className="p-3 bg-white rounded border border-green-200">
                        <p className="text-sm text-green-800">
                          ✓ Approuvé le{' '}
                          {format(new Date(msg.approval.approved_at), 'PPp', {
                            locale: fr,
                          })}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
