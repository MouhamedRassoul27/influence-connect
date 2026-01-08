"""
Pipeline IA complet - Orchestration de tous les services
"""

import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from models.schemas import ProcessedMessage, ClassificationOutput, DraftOutput, VerificationOutput
from services.classifier import ClassifierService
from services.rag import RAGService
from services.drafter import DrafterService
from services.verifier import VerifierService
from services.loreal_tools import LoreaToolService
from services.influencer_scoring import InfluencerScoringService
from config import settings, get_safe_autopilot_intents, get_critical_risk_flags

logger = logging.getLogger(__name__)

class AIPipeline:
    def __init__(
        self,
        classifier: ClassifierService,
        rag: RAGService,
        drafter: DrafterService,
        verifier: VerifierService
    ):
        self.classifier = classifier
        self.rag = rag
        self.drafter = drafter
        self.verifier = verifier
        self.loreal_tools = LoreaToolService()
        self.influencer_scorer = InfluencerScoringService()
        
    async def process(
        self,
        message: str,
        message_id: int,
        db: AsyncSession,
        context: dict = None
    ) -> ProcessedMessage:
        """
        Pipeline complet:
        1. Classify intent + risk
        2. Retrieve knowledge
        3. Draft reply
        4. Verify reply
        5. Determine HITL requirements
        """
        
        # 1. CLASSIFY
        logger.info(f"🔍 Step 1/4: Classifying...")
        classification = await self.classifier.classify(message, context)
        
        # Log classification
        await self._log_step(db, message_id, "classify", {
            "message": message,
            "context": context
        }, classification.dict(), self.classifier.model)
        
        # 2. RETRIEVE
        logger.info(f"📚 Step 2/4: Retrieving knowledge...")
        rag_extracts = await self.rag.retrieve(message, db, top_k=5)
        
        # 3. DRAFT
        logger.info(f"✍️  Step 3/4: Drafting reply...")
        draft = await self.drafter.draft(message, classification, rag_extracts, context)
        
        # Save draft to DB
        draft_id = await self._save_draft(
            db, message_id, draft, classification, rag_extracts
        )
        
        # Log draft
        await self._log_step(db, message_id, "draft", {
            "classification": classification.dict(),
            "rag_extracts": [e.dict() for e in rag_extracts]
        }, draft.dict(), self.drafter.model, draft_id)
        
        # 4. VERIFY
        logger.info(f"✅ Step 4/4: Verifying...")
        verification = await self.verifier.verify(draft, classification, message)
        
        # Log verification
        await self._log_step(db, message_id, "verify", {
            "draft": draft.dict()
        }, verification.dict(), self.verifier.model, draft_id)
        
        # 5. DETERMINE HITL vs AUTOPILOT
        requires_hitl, can_autopilot = self._determine_hitl(
            classification, verification
        )
        
        logger.info(f"📊 Pipeline complete: HITL={requires_hitl}, Autopilot={can_autopilot}")
        
        return ProcessedMessage(
            message_id=message_id,
            classification=classification,
            draft=draft,
            verification=verification,
            rag_extracts=[e.dict() for e in rag_extracts],
            requires_hitl=requires_hitl,
            can_autopilot=can_autopilot
        )
    
    def _determine_hitl(
        self,
        classification: ClassificationOutput,
        verification: VerificationOutput
    ) -> tuple[bool, bool]:
        """
        Determine if HITL required and if autopilot allowed
        """
        
        # Force HITL if env set
        if settings.hitl_required:
            return True, False
        
        # Escalate if critical risks
        critical_flags = get_critical_risk_flags()
        has_critical = any(flag in classification.risk_flags for flag in critical_flags)
        
        if has_critical:
            return True, False
        
        # Escalate if high/critical risk level
        if classification.risk_level in ["high", "critical"]:
            return True, False
        
        # Escalate if verification failed
        if verification.verdict in ["ESCALATE"]:
            return True, False
        
        # Check if intent is safe for autopilot
        safe_intents = get_safe_autopilot_intents()
        is_safe_intent = classification.intent in safe_intents
        
        # Autopilot allowed if:
        # - Safe intent
        # - High confidence
        # - Low risk
        # - Verification passed
        can_autopilot = (
            is_safe_intent
            and classification.intent_confidence >= 0.85
            and classification.risk_level == "low"
            and verification.verdict == "PASS"
        )
        
        requires_hitl = not can_autopilot
        
        return requires_hitl, can_autopilot
    
    async def _save_draft(
        self,
        db: AsyncSession,
        message_id: int,
        draft: DraftOutput,
        classification: ClassificationOutput,
        rag_extracts: list
    ) -> int:
        """Save draft to database"""
        
        result = await db.execute(
            text("""
                INSERT INTO drafts (
                    message_id,
                    reply_text,
                    ask_dm_question,
                    suggested_products,
                    suggested_influencers,
                    citations_internal,
                    confidence,
                    intent,
                    intent_confidence,
                    risk_flags,
                    risk_level,
                    rag_extracts,
                    requires_hitl,
                    can_autopilot
                )
                VALUES (
                    :message_id, :reply_text, :ask_dm_question, :suggested_products,
                    :suggested_influencers, :citations, :confidence, :intent,
                    :intent_confidence, :risk_flags, :risk_level, :rag_extracts,
                    :requires_hitl, :can_autopilot
                )
                RETURNING id
            """),
            {
                "message_id": message_id,
                "reply_text": draft.reply_text,
                "ask_dm_question": draft.ask_dm_question,
                "suggested_products": json.dumps([p.dict() for p in draft.suggested_products]),
                "suggested_influencers": draft.suggested_influencers,
                "citations": json.dumps([c.dict() for c in draft.citations_internal]),
                "confidence": draft.confidence,
                "intent": classification.intent,
                "intent_confidence": classification.intent_confidence,
                "risk_flags": classification.risk_flags,
                "risk_level": classification.risk_level,
                "rag_extracts": json.dumps([e.dict() if hasattr(e, 'dict') else e for e in rag_extracts]),
                "requires_hitl": True,
                "can_autopilot": False
            }
        )
        await db.commit()
        
        return result.scalar_one()
    
    async def _log_step(
        self,
        db: AsyncSession,
        message_id: int,
        log_type: str,
        input_data: dict,
        output_data: dict,
        model_used: str,
        draft_id: int = None
    ):
        """Log pipeline step for audit"""
        
        await db.execute(
            text("""
                INSERT INTO logs (message_id, draft_id, log_type, input_data, output_data, model_used)
                VALUES (:message_id, :draft_id, :log_type, :input_data, :output_data, :model_used)
            """),
            {
                "message_id": message_id,
                "draft_id": draft_id,
                "log_type": log_type,
                "input_data": json.dumps(input_data),
                "output_data": json.dumps(output_data),
                "model_used": model_used
            }
        )
        await db.commit()
    
    async def should_convert_to_dm(
        self,
        classification: ClassificationOutput,
        message: str,
        context: dict = None
    ) -> bool:
        """
        Determine if comment should be converted to DM
        Convert if: needs extended conversation, personal recommendation, product demo
        """
        dm_intents = {
            "recommendation",
            "routine_usage",
            "shade_color",
            "ingredients"
        }
        
        convert = classification.intent.value in dm_intents and classification.should_dm
        logger.info(f"{'📨' if convert else '💬'} Comment → DM: {convert}")
        return convert
    
    async def enrich_with_loreal_tools(
        self,
        draft: DraftOutput,
        classification: ClassificationOutput,
        db: AsyncSession
    ) -> DraftOutput:
        """Enhance draft with L'Oréal products and tools"""
        try:
            if classification.intent.value == "recommendation":
                products = await self.loreal_tools.recommend_products(
                    classification.reasoning
                )
                for p in products[:3]:
                    draft.suggested_products.append({
                        "name": p["name"],
                        "category": p["category"],
                        "price": p["price"],
                        "reason": "L'Oréal recommended"
                    })
                logger.info(f"✅ Added L'Oréal products")
            return draft
        except Exception as e:
            logger.warning(f"⚠️  Tool enrichment error: {e}")
            return draft
    
    async def analyze_for_ambassador(
        self,
        sender_id: str,
        sender_username: str,
        user_profile: dict = None
    ) -> dict:
        """Check if user qualifies for ambassador program"""
        try:
            if not user_profile:
                return {}
            
            profile = await self.influencer_scorer.analyze_user_profile(
                sender_id,
                user_profile
            )
            
            proposal = await self.influencer_scorer.propose_ambassador(profile)
            
            if proposal:
                logger.info(f"🌟 Ambassador opportunity: {sender_username}")
                return proposal.dict()
            
            return {}
        except Exception as e:
            logger.warning(f"⚠️  Ambassador error: {e}")
            return {}
