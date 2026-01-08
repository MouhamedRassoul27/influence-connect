-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Messages table (DM + Comments)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER,
    platform VARCHAR(20) NOT NULL,
    platform_message_id VARCHAR(255) UNIQUE,
    message_type VARCHAR(20) NOT NULL,
    sender_id VARCHAR(255) NOT NULL,
    sender_username VARCHAR(255),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_platform ON messages(platform, platform_message_id);

-- Threads table
CREATE TABLE IF NOT EXISTS threads (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    platform_thread_id VARCHAR(255) UNIQUE,
    participant_id VARCHAR(255) NOT NULL,
    participant_username VARCHAR(255),
    status VARCHAR(20) DEFAULT 'open',
    last_message_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_threads_status ON threads(status);
CREATE INDEX IF NOT EXISTS idx_threads_platform ON threads(platform, platform_thread_id);

-- Comments table  
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    platform VARCHAR(20) NOT NULL,
    platform_comment_id VARCHAR(255) UNIQUE,
    parent_comment_id INTEGER,
    author_id VARCHAR(255) NOT NULL,
    author_username VARCHAR(255),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_platform ON comments(platform, platform_comment_id);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    platform_post_id VARCHAR(255) UNIQUE,
    content TEXT,
    media_urls TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform, platform_post_id);

-- Drafts table
CREATE TABLE IF NOT EXISTS drafts (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    reply_text TEXT NOT NULL,
    ask_dm_question TEXT,
    suggested_products JSONB,
    suggested_influencers TEXT[],
    citations_internal JSONB,
    confidence FLOAT,
    intent VARCHAR(50),
    intent_confidence FLOAT,
    risk_level VARCHAR(20),
    risk_flags TEXT[],
    rag_extracts JSONB,
    verification_verdict VARCHAR(20),
    verification_issues JSONB,
    requires_hitl BOOLEAN DEFAULT TRUE,
    can_autopilot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_drafts_message ON drafts(message_id);
CREATE INDEX IF NOT EXISTS idx_drafts_hitl ON drafts(requires_hitl);

-- Approvals table
CREATE TABLE IF NOT EXISTS approvals (
    id SERIAL PRIMARY KEY,
    draft_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    edited_text TEXT,
    escalation_reason TEXT,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_approvals_draft ON approvals(draft_id);
CREATE INDEX IF NOT EXISTS idx_approvals_message ON approvals(message_id);

-- Influencers table
CREATE TABLE IF NOT EXISTS influencers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    instagram_handle VARCHAR(255) UNIQUE,
    tags JSONB,
    promo_code VARCHAR(50),
    commission_rate FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_influencers_handle ON influencers(instagram_handle);
CREATE INDEX IF NOT EXISTS idx_influencers_status ON influencers(status);

-- Knowledge docs table (RAG)
CREATE TABLE IF NOT EXISTS knowledge_docs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    doc_type VARCHAR(50),
    category VARCHAR(100),
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_docs 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_docs(doc_type);

-- Tracking events table
CREATE TABLE IF NOT EXISTS tracking_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    utm_content VARCHAR(100),
    influencer_id INTEGER,
    promo_code VARCHAR(50),
    product_id VARCHAR(100),
    value FLOAT,
    currency VARCHAR(10) DEFAULT 'EUR',
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_tracking_event_type ON tracking_events(event_type);
CREATE INDEX IF NOT EXISTS idx_tracking_influencer ON tracking_events(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_promo ON tracking_events(promo_code);

-- Logs table (audit trail)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    log_type VARCHAR(50) NOT NULL,
    message_id INTEGER,
    draft_id INTEGER,
    input_data JSONB,
    output_data JSONB,
    model_used VARCHAR(100),
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(log_type);
CREATE INDEX IF NOT EXISTS idx_logs_message ON logs(message_id);
CREATE INDEX IF NOT EXISTS idx_logs_draft ON logs(draft_id);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at);
