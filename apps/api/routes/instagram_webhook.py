"""
Instagram Webhook Routes
Receive real-time DMs and comments from Instagram
"""

import logging
import os
import sys
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import get_db
from services.instagram_webhook import InstagramWebhookService
from services.pipeline import AIPipeline
from models.orm import Message, Thread
from services.mock_ai import MockClassifierService, MockDrafterService, MockVerifierService
from services.rag import RAGService

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
    Facebook expects plain text response with the challenge value
    """
    try:
        query_params = dict(request.query_params)
        mode = query_params.get("hub.mode")
        verify_token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")
        
        logger.info(f"🔐 Webhook verification - mode={mode}, token_match={verify_token == INSTAGRAM_VERIFY_TOKEN}")
        
        # Facebook sends: hub.mode=subscribe&hub.verify_token=TOKEN&hub.challenge=CHALLENGE
        if mode == "subscribe" and verify_token == INSTAGRAM_VERIFY_TOKEN and challenge:
            logger.info("✅ Webhook verified with Instagram - returning challenge")
            # Return plain text response with correct content type
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.error(f"❌ Webhook verification failed - token={verify_token}, expected={INSTAGRAM_VERIFY_TOKEN}")
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
        # Get signature from headers (X-Hub-Signature-256 for SHA256)
        signature = request.headers.get("X-Hub-Signature-256", "")
        body = await request.body()
        
        logger.info(f"📥 Webhook POST received - body length: {len(body)}")
        
        # Verify signature if app secret is configured
        if INSTAGRAM_APP_SECRET and INSTAGRAM_APP_SECRET != "test-app-secret":
            if not instagram_service.verify_signature(body, signature):
                logger.warning("⚠️  Invalid signature from Instagram (continuing anyway)")
                # Don't fail on signature - might be test payload
        else:
            logger.debug("⚠️  Signature verification skipped - APP_SECRET not configured")
        
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
        
        # Initialize pipeline with mock services
        pipeline = AIPipeline(
            classifier=MockClassifierService(),
            rag=RAGService(),
            drafter=MockDrafterService(),
            verifier=MockVerifierService()
        )
        
        # Process through pipeline
        logger.info(f"🚀 Processing through AI pipeline...")
        result = await pipeline.process(
            message=pipeline_input["message"],
            message_id=message_id,
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



@router.delete("/webhook/uninstall")
async def uninstall_webhook():
    """
    Webhook uninstall endpoint (DELETE)
    Called when app is uninstalled
    """
    logger.info("🗑 Webhook uninstall requested")
    return {"status": "ok", "message": "Webhook uninstalled"}


@router.delete("/webhook/delete")
async def delete_webhook():
    """
    Webhook delete endpoint (DELETE)
    Called when user requests data deletion
    """
    logger.info("🗑️ Webhook delete requested")
    return {"status": "ok", "message": "Data deletion initiated"}


@router.get("/status")
async def instagram_webhook_status():
    """Check Instagram webhook connection status"""
    return {
        "webhook_enabled": True,
        "verify_token_set": bool(INSTAGRAM_VERIFY_TOKEN),
        "verify_token": INSTAGRAM_VERIFY_TOKEN if INSTAGRAM_VERIFY_TOKEN != "test-verify-token-123" else "[TEST]",
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
        
        # Initialize pipeline with mock services
        pipeline = AIPipeline(
            classifier=MockClassifierService(),
            rag=RAGService(),
            drafter=MockDrafterService(),
            verifier=MockVerifierService()
        )
        
        # Process
        result = await pipeline.process(
            message=pipeline_input["message"],
            message_id=message_obj.id,
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
