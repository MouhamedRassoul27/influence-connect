#!/bin/bash

# 🚀 Test Instagram Webhook Integration
# This script tests the Instagram webhook without needing a real Instagram account

API_URL="${1:-https://influence-connect-production.up.railway.app}"

echo "🧪 Testing Instagram Webhook Integration"
echo "=========================================="
echo "API: $API_URL"
echo ""

# Test 1: Check webhook status
echo "1️⃣ Checking webhook status..."
curl -s "$API_URL/api/instagram/status" | jq .
echo ""

# Test 2: Test with mock DM payload
echo "2️⃣ Testing with mock DM (skincare inquiry)..."
curl -s -X POST "$API_URL/api/instagram/test" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "messaging": [{
        "sender": {"id": "test_user_001", "name": "Sophie Martin"},
        "recipient": {"id": "loreal_beauty_account"},
        "message": {
          "mid": "msg_sk001",
          "text": "Bonjour! Jai la peau très sensible et reactif. Quel routine skincare me recommandez-vous? Surtout pour les rougeurs et la barrier cutanée."
        }
      }]
    }]
  }' | jq .
echo ""

# Test 3: Test with acne concern
echo "3️⃣ Testing with mock DM (acne & oil)..."
curl -s -X POST "$API_URL/api/instagram/test" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "messaging": [{
        "sender": {"id": "test_user_002", "name": "Antoine Dubois"},
        "recipient": {"id": "loreal_beauty_account"},
        "message": {
          "mid": "msg_acne002",
          "text": "Jai une peau très grasse avec beaucoup dimperfections. Comment je peux contrôler le sébum sans assécher ma peau?"
        }
      }]
    }]
  }' | jq .
echo ""

# Test 4: Test with aging concerns
echo "4️⃣ Testing with mock DM (anti-aging)..."
curl -s -X POST "$API_URL/api/instagram/test" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "messaging": [{
        "sender": {"id": "test_user_003", "name": "Valérie Leclerc"},
        "recipient": {"id": "loreal_beauty_account"},
        "message": {
          "mid": "msg_aging003",
          "text": "Je vois des rides et de la relâchement cutané. Que recommandez-vous pour rajeunir ma peau naturellement?"
        }
      }]
    }]
  }' | jq .
echo ""

# Test 5: Check messages in database
echo "5️⃣ Checking messages saved in database..."
curl -s "$API_URL/api/messages" | jq '.messages[] | {id, sender_name, content: .content[0:80]}' | head -20
echo ""

echo "✅ Tests complete!"
echo ""
echo "📊 Summary:"
echo "- Webhook status: Should be 'ready'"
echo "- DM tests: Should return 'success': true"
echo "- Messages: Should see new messages in database"
echo ""
echo "🔗 Next steps:"
echo "1. Get Instagram API credentials from https://developers.facebook.com"
echo "2. Set environment variables in Railway:"
echo "   - INSTAGRAM_VERIFY_TOKEN"
echo "   - INSTAGRAM_APP_SECRET"
echo "   - INSTAGRAM_ACCESS_TOKEN"
echo "   - INSTAGRAM_BUSINESS_ACCOUNT_ID"
echo "3. Configure webhook in Meta Developer Dashboard"
echo "4. Send real DM to your business account"
