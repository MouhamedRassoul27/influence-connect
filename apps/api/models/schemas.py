"""
Pydantic models pour validation JSON stricte
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

# ============================================================================
# Classification Output
# ============================================================================

class IntentEnum(str, Enum):
    AVAILABILITY = "availability"
    ROUTINE_USAGE = "routine_usage"
    SHADE_COLOR = "shade_color"
    DELIVERY_RETURN = "delivery_return"
    COMPLAINT = "complaint"
    WHERE_TO_BUY = "where_to_buy"
    INGREDIENTS = "ingredients"
    RECOMMENDATION = "recommendation"
    SPAM = "spam"
    UNKNOWN = "unknown"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ClassificationOutput(BaseModel):
    intent: IntentEnum
    intent_confidence: float = Field(ge=0.0, le=1.0)
    risk_flags: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    language: str = Field(default="fr")
    should_dm: bool = False
    should_escalate: bool = False
    reasoning: str = ""

# ============================================================================
# Draft Output
# ============================================================================

class SuggestedProduct(BaseModel):
    name: str
    category: str
    price: str
    reason: str

class Citation(BaseModel):
    source: str
    extract: str
    doc_id: int

class DraftOutput(BaseModel):
    reply_text: str = Field(max_length=500)
    ask_dm_question: Optional[str] = None
    suggested_products: List[SuggestedProduct] = Field(default_factory=list)
    suggested_influencers: List[str] = Field(default_factory=list)
    citations_internal: List[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)

# ============================================================================
# Verification Output
# ============================================================================

class VerdictEnum(str, Enum):
    PASS = "PASS"
    REWRITE = "REWRITE"
    ESCALATE = "ESCALATE"

class IssueType(str, Enum):
    TONE = "tone"
    COMPLIANCE = "compliance"
    FACTUAL = "factual"
    GRAMMAR = "grammar"
    LENGTH = "length"

class IssueSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class Issue(BaseModel):
    type: IssueType
    severity: IssueSeverity
    description: str
    location: str = ""

class VerificationOutput(BaseModel):
    verdict: VerdictEnum
    issues: List[Issue] = Field(default_factory=list)
    rewritten_reply_text: Optional[str] = None
    reasoning: str = ""

# ============================================================================
# API Request/Response Models
# ============================================================================

class IncomingMessage(BaseModel):
    """Message entrant (DM ou comment)"""
    platform: str = "instagram"
    message_type: str = "dm"  # 'dm', 'comment', 'reply'
    sender_id: str
    sender_username: Optional[str] = None
    content: str
    thread_id: Optional[int] = None
    comment_id: Optional[int] = None
    metadata: dict = Field(default_factory=dict)

class ProcessedMessage(BaseModel):
    """Message après pipeline complet"""
    message_id: int
    classification: ClassificationOutput
    draft: DraftOutput
    verification: VerificationOutput
    rag_extracts: List[dict] = Field(default_factory=list)
    requires_hitl: bool = True
    can_autopilot: bool = False

class ApprovalAction(BaseModel):
    """Action HITL"""
    draft_id: int
    approved_by: str
    action: str  # 'approved', 'edited', 'rejected', 'escalated'
    final_text: Optional[str] = None
    edited_text: Optional[str] = None
    notes: Optional[str] = None

# ============================================================================
# Influencer Models
# ============================================================================

class InfluencerTags(BaseModel):
    undertone: Optional[str] = None  # 'warm', 'cool', 'neutral'
    hair_type: Optional[str] = None  # 'straight', 'wavy', 'curly', 'coily'
    color_goal: Optional[str] = None  # 'blonde', 'brunette', 'red', 'silver'
    locale: str = "fr"
    formats: List[str] = Field(default_factory=list)  # ['reels', 'stories', 'posts']

class Influencer(BaseModel):
    id: Optional[int] = None
    name: str
    instagram_handle: str
    tiktok_handle: Optional[str] = None
    email: Optional[str] = None
    tags: InfluencerTags
    promo_code: Optional[str] = None
    commission_rate: float = 0.10
    status: str = "active"

# ============================================================================
# Knowledge Document Models
# ============================================================================

class KnowledgeDoc(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    doc_type: str  # 'policy', 'faq', 'product', 'claim'
    category: Optional[str] = None
    source_file: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class RAGExtract(BaseModel):
    """Extrait retourné par RAG"""
    doc_id: int
    title: str
    content: str
    similarity_score: float
    doc_type: str
    category: Optional[str] = None
