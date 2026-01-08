"""
Routes pour commentaires et ambassadeurs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json

from config import settings
from db.database import get_db
from models.schemas import IncomingMessage, ProcessedMessage
from services.pipeline import AIPipeline
from services.mock_ai import MockClassifierService, MockDrafterService, MockVerifierService
from services.rag import RAGService
from services.influencer_scoring import InfluencerScoringService, InfluencerProfile

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
if settings.anthropic_api_key:
    from services.real_ai import RealClassifierService, RealDrafterService, RealVerifierService
    classifier_service = RealClassifierService()
    drafter_service = RealDrafterService()
    verifier_service = RealVerifierService()
else:
    classifier_service = MockClassifierService()
    drafter_service = MockDrafterService()
    verifier_service = MockVerifierService()

rag_service = RAGService()
pipeline = AIPipeline(classifier_service, rag_service, drafter_service, verifier_service)
influencer_service = InfluencerScoringService()

@router.post("/comments/process", response_model=ProcessedMessage)
async def process_comment(
    message: IncomingMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    Process Instagram/Facebook comment:
    1. Save comment to DB
    2. Run AI pipeline
    3. Determine if should convert to DM
    4. Return draft response
    """
    try:
        logger.info(f"💬 Processing comment from {message.sender_username}: {message.content[:50]}...")
        
        # Save comment
        result = await db.execute(
            text("""
                INSERT INTO messages (platform, message_type, sender_id, sender_username, content, thread_id, meta)
                VALUES (:platform, :message_type, :sender_id, :sender_username, :content, :thread_id, :meta)
                RETURNING id
            """),
            {
                "platform": message.platform,
                "message_type": "comment",
                "sender_id": message.sender_id,
                "sender_username": message.sender_username,
                "content": message.content,
                "thread_id": message.thread_id,
                "meta": json.dumps(message.metadata) if message.metadata else '{}'
            }
        )
        await db.commit()
        message_id = result.scalar_one()
        
        # Run pipeline
        processed = await pipeline.process(message.content, message_id, db, message.metadata)
        
        # Check if should convert to DM
        should_dm = await pipeline.should_convert_to_dm(
            processed.classification,
            message.content,
            message.metadata
        )
        
        # Add DM conversion flag
        processed.can_autopilot = False  # Comments always need manual review
        processed.requires_hitl = True
        
        logger.info(f"✅ Comment {message_id} processed: convert_to_dm={should_dm}")
        
        return processed
        
    except Exception as e:
        logger.error(f"❌ Error processing comment: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/influencers/analyze")
async def analyze_influencer(
    influencer_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze user for ambassador program
    Input: user_id, username, followers_count, engagement_rate, content_categories
    """
    try:
        user_id = influencer_data.get("user_id")
        username = influencer_data.get("username")
        
        if not user_id or not username:
            raise HTTPException(status_code=400, detail="Missing user_id or username")
        
        logger.info(f"🔍 Analyzing influencer: {username}")
        
        # Analyze profile
        profile = await influencer_service.analyze_user_profile(user_id, influencer_data)
        
        # Generate proposal if eligible
        proposal = await influencer_service.propose_ambassador(profile)
        
        response = {
            "user_id": user_id,
            "username": username,
            "analysis": {
                "followers": profile.followers_count,
                "engagement_rate": f"{profile.engagement_rate*100:.1f}%",
                "ambassador_score": f"{profile.ambassador_score:.1f}/100",
                "eligible": proposal is not None
            }
        }
        
        if proposal:
            response["proposal"] = proposal.dict()
            logger.info(f"✅ Generated ambassador proposal for {username}")
        else:
            logger.info(f"⚠️  User not eligible for ambassador program")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error analyzing influencer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ambassadors/propose")
async def propose_ambassador_program(
    proposal_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Send ambassador program proposal to influencer
    """
    try:
        user_id = proposal_data.get("user_id")
        username = proposal_data.get("username")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        logger.info(f"📨 Proposing ambassador program to {username}")
        
        # Save proposal
        result = await db.execute(
            text("""
                INSERT INTO influencers (platform, platform_influencer_id, username, meta)
                VALUES (:platform, :platform_influencer_id, :username, :meta)
                RETURNING id
            """),
            {
                "platform": proposal_data.get("platform", "instagram"),
                "platform_influencer_id": user_id,
                "username": username,
                "meta": json.dumps(proposal_data)
            }
        )
        await db.commit()
        influencer_id = result.scalar_one()
        
        return {
            "status": "proposal_sent",
            "influencer_id": influencer_id,
            "username": username,
            "message": f"Ambassador proposal sent to {username}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error proposing ambassador: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/influencers/{influencer_id}")
async def get_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get influencer profile"""
    try:
        result = await db.execute(
            text("SELECT * FROM influencers WHERE id = :id"),
            {"id": influencer_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Influencer not found")
        
        return {
            "id": row[0],
            "username": row[3],
            "followers": row[5],
            "engagement_rate": row[6],
            "categories": row[7]
        }
    except Exception as e:
        logger.error(f"❌ Error fetching influencer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
