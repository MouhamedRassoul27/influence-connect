"""
Instagram Webhook Routes
Receive real-time DMs and comments from Instagram
"""

import logging
import os
import sys
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import get_db
from services.instagram_webhook import InstagramWebhookService
from services.pipeline import AIPipeline
from models.orm import Message, Thread
from services.classifier import ClassifierService
from services.rag import RAGService
from services.drafter import DrafterService
from services.verifier import VerifierService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/instagram", tags=["instagram"])

# Initialize Instagram Webhook Service
INSTAGRAM_VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "test-verify-token-123")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "test-app-secret")

instagram_service = InstagramWebhookService(
    verify_token=INSTAGRAM_VERIFY_TOKEN,
    app_secret=INSTAGRAM_APP_SECRET
)


@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint (GET)
    Instagram calls this to verify webhook is active
    """
    try:
        query_params = dict(request.query_params)
        challenge = instagram_service.verify_webhook(query_params)
        
        if challenge:
            logger.info("✅ Webhook verified with Instagram")
            return challenge
        else:
            logger.error("❌ Webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        logger.error(f"❌ Verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Webhook event receiver (POST)
    Instagram sends DMs and comments here
    """
    try:
        # Get signature from headers
        signature = request.headers.get("X-Hub-Signature", "")
        body = await request.body()
        
        # Verify signature
        if not instagram_service.verify_signature(body, signature):
            logger.error("❌ Invalid signature from Instagram")
            # Still return 200 to prevent retries, but log the error
            return {"status": "error", "reason": "Invalid signature"}
        
        # Parse JSON
        data = await request.json()
        logger.info(f"📥 Webhook event received: {data.get('object')}")
        
        # Parse webhook event
        webhook_event = instagram_service.parse_webhook_event(data)
        if not webhook_event:
            logger.warning("⚠️ No processable event found in webhook")
            return {"status": "ok", "processed": False}
        
        # Convert to pipeline format
        pipeline_input = instagram_service.format_for_pipeline(webhook_event)
        
        # Save to database as message
        message_obj = Message(
            platform="instagram",
            platform_message_id=webhook_event.get("message_id"),
            message_type="dm" if webhook_event.get("event_type") == "dm" else "comment",
            sender_id=pipeline_input["user_id"],
            sender_username=pipeline_input["user_name"],
            content=pipeline_input["message"],
            meta=pipeline_input["meta"]
        )
        db.add(message_obj)
        await db.commit()
        
        message_id = message_obj.id
        logger.info(f"💾 Saved message to DB: id={message_id}")
        
        # Initialize pipeline
        pipeline = AIPipeline(
            classifier=ClassifierService(),
            rag=RAGService(),
            drafter=DrafterService(),
            verifier=VerifierService()
        )
        
        # Process through pipeline
        logger.info(f"🚀 Processing through AI pipeline...")
        result = await pipeline.process(
            message=pipeline_input["message"],
            sender_id=pipeline_input["user_id"],
            thread_id=pipeline_input["thread_id"],
            db=db
        )
        
        logger.info(f"✅ Processing complete: verdict={result.get('verification_verdict')}")
        
        return {
            "status": "ok",
            "processed": True,
            "message_id": message_id,
            "event_type": webhook_event.get("event_type"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}", exc_info=True)
        # Return 200 to prevent Instagram retries, but log the error
        return {"status": "error", "reason": str(e)}


@router.get("/status")
async def instagram_webhook_status():
    """Check Instagram webhook connection status"""
    return {
        "webhook_enabled": True,
        "verify_token_set": bool(INSTAGRAM_VERIFY_TOKEN),
        "app_secret_set": bool(INSTAGRAM_APP_SECRET),
        "status": "ready"
    }


@router.post("/test")
async def test_webhook(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    Test webhook with mock Instagram payload
    Useful for local testing without real Instagram account
    """
    try:
        logger.info(f"🧪 Testing with payload: {payload}")
        
        webhook_event = instagram_service.parse_webhook_event(payload)
        if not webhook_event:
            return {"error": "Invalid payload"}
        
        pipeline_input = instagram_service.format_for_pipeline(webhook_event)
        
        # Save message
        message_obj = Message(
            platform="instagram",
            platform_message_id=webhook_event.get("message_id"),
            message_type="dm" if webhook_event.get("event_type") == "dm" else "comment",
            sender_id=pipeline_input["user_id"],
            sender_username=pipeline_input["user_name"],
            content=pipeline_input["message"],
            meta=pipeline_input["meta"]
        )
        db.add(message_obj)
        await db.commit()
        
        # Initialize pipeline
        pipeline = AIPipeline(
            classifier=ClassifierService(),
            rag=RAGService(),
            drafter=DrafterService(),
            verifier=VerifierService()
        )
        
        # Process
        result = await pipeline.process(
            message=pipeline_input["message"],
            sender_id=pipeline_input["user_id"],
            thread_id=pipeline_input["thread_id"],
            db=db
        )
        
        return {
            "success": True,
            "message_id": message_obj.id,
            "event_type": webhook_event.get("event_type"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return {"error": str(e)}
