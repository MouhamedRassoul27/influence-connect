"""
Routes pour le flux messages (pipeline IA complet)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json

from config import settings
from db.database import get_db
from models.schemas import IncomingMessage, ProcessedMessage, ApprovalAction
from services.pipeline import AIPipeline
from services.rag import RAGService

router = APIRouter()
logger = logging.getLogger(__name__)

# Use real Claude models if API key is available, otherwise use mocks
if settings.anthropic_api_key:
    logger.info("✅ Using REAL Claude AI services")
    from services.real_ai import RealClassifierService, RealDrafterService, RealVerifierService
    classifier_service = RealClassifierService()
    drafter_service = RealDrafterService()
    verifier_service = RealVerifierService()
else:
    logger.info("⚠️  Using MOCK AI services (no ANTHROPIC_API_KEY set)")
    from services.mock_ai import MockClassifierService, MockDrafterService, MockVerifierService
    classifier_service = MockClassifierService()
    drafter_service = MockDrafterService()
    verifier_service = MockVerifierService()

rag_service = RAGService()
pipeline = AIPipeline(classifier_service, rag_service, drafter_service, verifier_service)

@router.post("/process", response_model=ProcessedMessage)
async def process_message(
    message: IncomingMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    Pipeline IA complet pour un message entrant:
    1. Save message to DB
    2. Classify intent + risk
    3. Retrieve knowledge (RAG)
    4. Draft reply
    5. Verify reply
    6. Return for HITL
    """
    try:
        logger.info(f"📥 Processing message from {message.sender_username}: {message.content[:50]}...")
        
        # 1. Save message
        result = await db.execute(
            text("""
                INSERT INTO messages (platform, message_type, sender_id, sender_username, content, thread_id, meta)
                VALUES (:platform, :message_type, :sender_id, :sender_username, :content, :thread_id, :meta)
                RETURNING id
            """),
            {
                "platform": message.platform,
                "message_type": message.message_type,
                "sender_id": message.sender_id,
                "sender_username": message.sender_username,
                "content": message.content,
                "thread_id": message.thread_id,
                "meta": json.dumps(message.metadata) if message.metadata else '{}'
            }
        )
        await db.commit()
        message_id = result.scalar_one()
        
        # 2-5. Pipeline IA
        processed = await pipeline.process(message.content, message_id, db)
        
        logger.info(f"✅ Message {message_id} processed: intent={processed.classification.intent}, verdict={processed.verification.verdict}")
        
        return processed
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve")
async def approve_draft(
    approval: ApprovalAction,
    db: AsyncSession = Depends(get_db)
):
    """
    HITL: Approve/Edit/Escalate a draft
    """
    try:
        # Save approval
        await db.execute(
            text("""
                INSERT INTO approvals (draft_id, approved_by, action, final_text, edited_text, notes)
                VALUES (:draft_id, :approved_by, :action, :final_text, :edited_text, :notes)
            """),
            {
                "draft_id": approval.draft_id,
                "approved_by": approval.approved_by,
                "action": approval.action,
                "final_text": approval.final_text,
                "edited_text": approval.edited_text,
                "notes": approval.notes
            }
        )
        await db.commit()
        
        # TODO: If approved, send to Meta API
        
        logger.info(f"✅ Draft {approval.draft_id} {approval.action} by {approval.approved_by}")
        
        return {
            "status": "success",
            "action": approval.action,
            "message": f"Draft {approval.action} successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error approving draft: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inbox")
async def get_inbox(
    status: str = "open",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get inbox threads for HITL console"""
    result = await db.execute(
        text("""
            SELECT t.*, m.content as last_message, m.created_at as last_message_at
            FROM threads t
            LEFT JOIN messages m ON m.thread_id = t.id
            WHERE t.status = :status
            ORDER BY t.last_message_at DESC
            LIMIT :limit
        """),
        {"status": status, "limit": limit}
    )
    
    threads = [dict(row._mapping) for row in result]
    return {"threads": threads, "count": len(threads)}

@router.get("/thread/{thread_id}")
async def get_thread(
    thread_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get thread details with messages and drafts"""
    # Messages
    messages_result = await db.execute(
        text("""
            SELECT * FROM messages
            WHERE thread_id = :thread_id
            ORDER BY created_at ASC
        """),
        {"thread_id": thread_id}
    )
    messages = [dict(row._mapping) for row in messages_result]
    
    # Drafts
    drafts_result = await db.execute(
        text("""
            SELECT d.*, a.action as approval_action, a.final_text
            FROM drafts d
            LEFT JOIN approvals a ON a.draft_id = d.id
            WHERE d.message_id IN (SELECT id FROM messages WHERE thread_id = :thread_id)
            ORDER BY d.created_at DESC
        """),
        {"thread_id": thread_id}
    )
    drafts = [dict(row._mapping) for row in drafts_result]
    
    return {
        "thread_id": thread_id,
        "messages": messages,
        "drafts": drafts
    }
