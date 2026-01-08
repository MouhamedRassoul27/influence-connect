import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Messages API
// ============================================================================

export interface ProcessedMessage {
  message_id: number;
  classification: {
    intent: string;
    intent_confidence: number;
    risk_flags: string[];
    risk_level: string;
    language: string;
    should_dm: boolean;
    should_escalate: boolean;
  };
  draft: {
    reply_text: string;
    ask_dm_question?: string;
    suggested_products: Array<{
      product_id: string;
      name: string;
      description: string;
      price: number;
    }>;
    suggested_influencers: number[];
    citations_internal: Array<{
      doc_id: number;
      title: string;
      excerpt: string;
    }>;
    confidence: number;
  };
  verification: {
    verdict: 'PASS' | 'REWRITE' | 'ESCALATE';
    issues: Array<{
      issue_type: string;
      severity: string;
      description: string;
    }>;
    rewritten_reply_text?: string;
  };
  requires_hitl: boolean;
  can_autopilot: boolean;
  processing_time_seconds: number;
}

export interface ApprovalAction {
  action: 'approve' | 'edit' | 'escalate';
  edited_text?: string;
  escalation_reason?: string;
}

export const messagesAPI = {
  process: (content: string, threadId?: number, commentId?: number) =>
    api.post<ProcessedMessage>('/api/messages/process', {
      content,
      thread_id: threadId,
      comment_id: commentId,
      platform: 'instagram',
    }),

  approve: (messageId: number, draftId: number, action: ApprovalAction) =>
    api.post('/api/messages/approve', {
      message_id: messageId,
      draft_id: draftId,
      ...action,
    }),

  getInbox: (status?: string, limit = 50) =>
    api.get('/api/messages/inbox', { params: { status, limit } }),

  getThread: (threadId: number) =>
    api.get(`/api/messages/thread/${threadId}`),
};

// ============================================================================
// Influencers API
// ============================================================================

export interface Influencer {
  id: number;
  name: string;
  instagram_handle: string;
  tags: {
    undertone?: string;
    hair_type?: string;
    color_goal?: string;
    locale?: string;
    formats?: string[];
  };
  promo_code?: string;
  commission_rate: number;
  status: string;
}

export const influencersAPI = {
  list: (status = 'active') =>
    api.get<Influencer[]>('/api/influencers/', { params: { status } }),

  get: (id: number) => api.get<Influencer>(`/api/influencers/${id}`),

  create: (data: Omit<Influencer, 'id'>) =>
    api.post<Influencer>('/api/influencers/', data),

  update: (id: number, data: Partial<Influencer>) =>
    api.put<Influencer>(`/api/influencers/${id}`, data),
};

// ============================================================================
// Tracking API
// ============================================================================

export const trackingAPI = {
  trackEvent: (data: {
    event_type: string;
    utm_source?: string;
    utm_medium?: string;
    utm_campaign?: string;
    utm_content?: string;
    influencer_id?: number;
    promo_code?: string;
    product_id?: string;
    value?: number;
    currency?: string;
  }) => api.post('/api/tracking/event', data),

  getStats: (influencerId?: number, days = 30) =>
    api.get('/api/tracking/stats', {
      params: { influencer_id: influencerId, days },
    }),
};

// ============================================================================
// Eval API
// ============================================================================

export const evalAPI = {
  getMetrics: (days = 7) =>
    api.get('/api/eval/metrics', { params: { days } }),

  getLogs: (logType?: string, limit = 100) =>
    api.get('/api/eval/logs', { params: { log_type: logType, limit } }),
};

export default api;
