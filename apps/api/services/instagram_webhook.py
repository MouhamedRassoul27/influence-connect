"""
Instagram Webhook Integration
Receives real-time DMs and comments from Instagram Business Account
"""

import hashlib
import hmac
import logging
import json
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class InstagramWebhookService:
    """
    Handles Instagram webhook events
    - Webhook verification (GET request)
    - Message reception (POST request)
    - Event routing to pipeline
    """
    
    def __init__(self, verify_token: str, app_secret: str):
        """
        Args:
            verify_token: Your custom verification token (set in Instagram app settings)
            app_secret: Your Instagram App Secret
        """
        self.verify_token = verify_token
        self.app_secret = app_secret
        logger.info("✅ Instagram Webhook Service initialized")
    
    def verify_webhook(self, query_params: Dict[str, str]) -> Optional[str]:
        """
        Verify webhook from Instagram (GET request)
        
        Instagram sends: hub.mode, hub.challenge, hub.verify_token
        We respond with the challenge if token matches
        """
        try:
            mode = query_params.get("hub.mode")
            token = query_params.get("hub.verify_token")
            challenge = query_params.get("hub.challenge")
            
            logger.info(f"🔐 Webhook verification request: mode={mode}, token={'***' if token else None}")
            
            if mode == "subscribe" and token == self.verify_token:
                logger.info("✅ Webhook verification SUCCESS")
                return challenge
            else:
                logger.error("❌ Webhook verification FAILED: token mismatch")
                return None
                
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Instagram (POST request)
        
        Instagram sends X-Hub-Signature header with HMAC-SHA256 signature
        """
        try:
            expected_sig = "sha1=" + hmac.new(
                self.app_secret.encode(),
                payload,
                hashlib.sha1
            ).hexdigest()
            
            is_valid = hmac.compare_digest(signature, expected_sig)
            logger.info(f"🔐 Signature verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Signature verification error: {e}")
            return False
    
    def parse_webhook_event(self, data: Dict) -> Optional[Dict]:
        """
        Parse incoming Instagram webhook event
        
        Returns structured message event:
        {
            "event_type": "message" | "comment",
            "source": "instagram",
            "message_id": str,
            "sender_id": str,
            "sender_name": str,
            "recipient_id": str,
            "text": str,
            "media": {...} | None,
            "timestamp": datetime,
            "raw": original event data
        }
        """
        try:
            if data.get("object") != "instagram":
                logger.warning(f"⚠️ Unknown object type: {data.get('object')}")
                return None
            
            entries = data.get("entry", [])
            if not entries:
                return None
            
            for entry in entries:
                messaging = entry.get("messaging", [])
                for msg in messaging:
                    event = self._parse_message_event(msg)
                    if event:
                        return event
            
            # Also check for comments
            changes = entry[0].get("changes", []) if entries else []
            for change in changes:
                event = self._parse_comment_event(change)
                if event:
                    return event
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Event parsing error: {e}")
            return None
    
    def _parse_message_event(self, msg: Dict) -> Optional[Dict]:
        """Parse DM event"""
        try:
            sender = msg.get("sender", {})
            recipient = msg.get("recipient", {})
            message = msg.get("message", {})
            
            if not message:
                return None
            
            text = message.get("text", "")
            media = message.get("attachments")
            
            if not text and not media:
                return None
            
            event = {
                "event_type": "dm",
                "source": "instagram",
                "message_id": message.get("mid"),
                "sender_id": sender.get("id"),
                "sender_name": sender.get("name"),
                "recipient_id": recipient.get("id"),
                "text": text,
                "media": media,
                "timestamp": datetime.now().isoformat(),
                "raw": msg
            }
            
            logger.info(f"📨 DM Event: from={event['sender_name']}, text={text[:50]}...")
            return event
            
        except Exception as e:
            logger.error(f"❌ Message parsing error: {e}")
            return None
    
    def _parse_comment_event(self, change: Dict) -> Optional[Dict]:
        """Parse comment event"""
        try:
            field = change.get("field")
            value = change.get("value", {})
            
            if field != "comments":
                return None
            
            event = {
                "event_type": "comment",
                "source": "instagram",
                "message_id": value.get("id"),
                "sender_id": value.get("from", {}).get("id"),
                "sender_name": value.get("from", {}).get("name"),
                "recipient_id": value.get("media_product_type"),
                "text": value.get("text"),
                "timestamp": datetime.now().isoformat(),
                "raw": value
            }
            
            logger.info(f"💬 Comment Event: from={event['sender_name']}, text={event['text'][:50]}...")
            return event
            
        except Exception as e:
            logger.error(f"❌ Comment parsing error: {e}")
            return None
    
    def format_for_pipeline(self, webhook_event: Dict) -> Dict:
        """Convert Instagram webhook event to pipeline format"""
        return {
            "source": "instagram",
            "event_type": webhook_event.get("event_type"),
            "user_id": webhook_event.get("sender_id"),
            "user_name": webhook_event.get("sender_name"),
            "message": webhook_event.get("text"),
            "thread_id": webhook_event.get("message_id"),
            "timestamp": webhook_event.get("timestamp"),
            "requires_hitl": False,
            "meta": {
                "instagram_message_id": webhook_event.get("message_id"),
                "instagram_sender_id": webhook_event.get("sender_id"),
                "instagram_recipient_id": webhook_event.get("recipient_id"),
                "instagram_media": webhook_event.get("media"),
                "raw_event": webhook_event.get("raw")
            }
        }


# Instagram App Setup Instructions
INSTAGRAM_SETUP_GUIDE = """
🔗 INSTAGRAM WEBHOOK SETUP GUIDE
==================================

1. CREATE INSTAGRAM APP (Meta Developer)
   - Go to: https://developers.facebook.com/
   - Create App → Select "Business" type
   - App Name: "Influence Connect"
   - App Purpose: "Business"

2. GET YOUR CREDENTIALS
   - App ID: (shown in Settings)
   - App Secret: (shown in Settings)
   - Access Token: (generate in Roles → Developers)

3. SET WEBHOOK CALLBACK URL
   - Production: https://influence-connect-production.up.railway.app/api/instagram/webhook
   - Local testing: Use ngrok for tunneling
     $ ngrok http 8000
     → Use ngrok URL in webhook settings

4. SUBSCRIBE TO WEBHOOK EVENTS
   - Fields: messages, message_echoes, comments
   - Verify Token: Create your own (e.g., "your-secret-verify-token-123")

5. SET ENVIRONMENT VARIABLES in Railway:
   - INSTAGRAM_VERIFY_TOKEN=your-secret-verify-token-123
   - INSTAGRAM_APP_SECRET=your-app-secret
   - INSTAGRAM_ACCESS_TOKEN=your-access-token
   - INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id

6. TEST WEBHOOK
   - In Meta Developer console: Test Webhook
   - Should see: ✅ Webhook verified
   
7. ACTIVATE BUSINESS ACCOUNT
   - Link your Instagram Business Account to the app
   - Grant permissions: instagram_business_basic, instagram_basic

8. SEND TEST MESSAGE
   - DM your business account from personal account
   - Watch logs: should see "📨 DM Event" message

WEBHOOK PAYLOAD EXAMPLES:
========================

DM EVENT:
{
  "object": "instagram",
  "entry": [{
    "id": "1234567890",
    "messaging": [{
      "sender": {"id": "user123", "name": "John Doe"},
      "recipient": {"id": "business123"},
      "message": {
        "mid": "msg123",
        "text": "I love your products!",
        "attachments": null
      }
    }]
  }]
}

COMMENT EVENT:
{
  "object": "instagram",
  "entry": [{
    "changes": [{
      "field": "comments",
      "value": {
        "id": "comment123",
        "text": "Amazing! 😍",
        "from": {"id": "user456", "name": "Jane Smith"},
        "media_product_type": "FEED"
      }
    }]
  }]
}

TEST CURL COMMAND:
==================
curl -X POST https://influence-connect-production.up.railway.app/api/instagram/webhook \\
  -H "Content-Type: application/json" \\
  -H "X-Hub-Signature: sha1=..." \\
  -d '{
    "object": "instagram",
    "entry": [{
      "messaging": [{
        "sender": {"id": "test123", "name": "Test User"},
        "recipient": {"id": "business123"},
        "message": {
          "mid": "msg_test",
          "text": "Testing webhook!"
        }
      }]
    }]
  }'
"""
