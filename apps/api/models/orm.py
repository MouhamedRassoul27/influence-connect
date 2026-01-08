"""
SQLAlchemy ORM Models - defines database schema
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Message(Base):
    """DMs and Comments"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, nullable=True)
    platform = Column(String(20), nullable=False)
    platform_message_id = Column(String(255), unique=True, nullable=True)
    message_type = Column(String(20), nullable=False)
    sender_id = Column(String(255), nullable=False)
    sender_username = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_messages_thread', 'thread_id'),
        Index('idx_messages_platform', 'platform', 'platform_message_id'),
    )

class Thread(Base):
    """Conversation threads"""
    __tablename__ = "threads"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)
    platform_thread_id = Column(String(255), unique=True, nullable=True)
    participant_id = Column(String(255), nullable=False)
    participant_username = Column(String(255), nullable=True)
    status = Column(String(20), default='open')
    last_message_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_threads_status', 'status'),
        Index('idx_threads_platform', 'platform', 'platform_thread_id'),
    )

class Draft(Base):
    """AI-generated drafts for review"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    reply_text = Column(Text, nullable=False)
    ask_dm_question = Column(Text, nullable=True)
    suggested_products = Column(JSON, nullable=True)
    suggested_influencers = Column(ARRAY(String), nullable=True)
    citations_internal = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    intent = Column(String(50), nullable=True)
    intent_confidence = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    risk_flags = Column(ARRAY(String), nullable=True)
    rag_extracts = Column(JSON, nullable=True)
    verification_verdict = Column(String(20), nullable=True)
    verification_issues = Column(JSON, nullable=True)
    requires_hitl = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON, nullable=True)

class Approval(Base):
    """HITL approvals"""
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True)
    draft_id = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')
    moderator_id = Column(String(255), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    approved_text = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime, nullable=True)

class Influencer(Base):
    """Influencer recommendations"""
    __tablename__ = "influencers"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)
    platform_influencer_id = Column(String(255), unique=True, nullable=True)
    username = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    followers_count = Column(Integer, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON, nullable=True)

class KnowledgeDoc(Base):
    """Knowledge base documents for RAG"""
    __tablename__ = "knowledge_docs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON, nullable=True)

class TrackingEvent(Base):
    """Analytics and tracking"""
    __tablename__ = "tracking_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    message_id = Column(Integer, nullable=True)
    draft_id = Column(Integer, nullable=True)
    approval_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Log(Base):
    """Logging"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=True)
    draft_id = Column(Integer, nullable=True)
    log_type = Column(String(50), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    model_used = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
