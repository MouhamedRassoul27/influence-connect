"""
Real Anthropic AI Services - using Claude models
"""

import logging
from anthropic import Anthropic
from models.schemas import ClassificationOutput, IntentEnum, RiskLevel, DraftOutput, VerificationOutput

logger = logging.getLogger(__name__)

client = Anthropic()

class RealClassifierService:
    """Classify message intent and detect risks using Claude"""
    
    def __init__(self):
        self.model = "claude-haiku-4-5-20251001"
    
    async def classify(self, message: str, context: dict = None) -> ClassificationOutput:
        """Classify message intent and risk level"""
        try:
            prompt = f"""Analyze this customer message and classify it.

Message: "{message}"

Respond with JSON only:
{{
  "intent": "recommendation|availability|routine_usage|shade_color|delivery_return|complaint|where_to_buy|ingredients|spam|unknown",
  "intent_confidence": 0.0-1.0,
  "risk_flags": ["list of risk flags if any"],
  "risk_level": "low|medium|high|critical",
  "language": "fr",
  "should_dm": true/false,
  "should_escalate": false,
  "reasoning": "brief explanation"
}}"""
            
            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            response_text = response.content[0].text
            # Extract JSON from response
            try:
                data = json.loads(response_text)
            except:
                # If response contains markdown code blocks, extract JSON
                if "```json" in response_text:
                    data = json.loads(response_text.split("```json")[1].split("```")[0])
                else:
                    data = json.loads(response_text.split("```")[1].split("```")[0])
            
            return ClassificationOutput(
                intent=IntentEnum(data["intent"]),
                intent_confidence=data["intent_confidence"],
                risk_flags=data.get("risk_flags", []),
                risk_level=RiskLevel(data["risk_level"]),
                language=data.get("language", "fr"),
                should_dm=data.get("should_dm", False),
                should_escalate=data.get("should_escalate", False),
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            logger.error(f"❌ Classification error: {e}")
            # Fallback to safe defaults
            return ClassificationOutput(
                intent=IntentEnum.UNKNOWN,
                intent_confidence=0.0,
                risk_flags=[],
                risk_level=RiskLevel.MEDIUM,
                reasoning=f"Error: {str(e)}"
            )


class RealDrafterService:
    """Generate reply using Claude"""
    
    def __init__(self):
        self.model = "claude-sonnet-4-5-20250929"
    
    async def draft(self, message: str, intent: str, rag_docs: list = None) -> DraftOutput:
        """Draft a reply to the customer message"""
        try:
            context = ""
            if rag_docs:
                context = "Knowledge base extracts:\n" + "\n".join([f"- {doc}" for doc in rag_docs])
            
            prompt = f"""You are a friendly L'Oréal beauty advisor. Reply to this customer message in French.

Customer: "{message}"
Intent: {intent}
{context}

Generate a helpful, professional response that:
1. Addresses their concern
2. Suggests relevant products if appropriate
3. Is friendly and conversational
4. Asks a follow-up question if needed

Keep response to 1-2 sentences maximum."""
            
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            reply_text = response.content[0].text
            
            return DraftOutput(
                reply_text=reply_text,
                ask_dm_question="Avez-vous d'autres questions?" if "?" not in reply_text else None,
                suggested_products=[],
                suggested_influencers=[],
                citations_internal=[],
                confidence=0.85
            )
        except Exception as e:
            logger.error(f"❌ Draft error: {e}")
            return DraftOutput(
                reply_text="Merci pour votre message! Notre équipe vous répondra très bientôt.",
                ask_dm_question=None,
                suggested_products=[],
                suggested_influencers=[],
                citations_internal=[],
                confidence=0.5
            )


class RealVerifierService:
    """Verify reply for brand safety using Claude"""
    
    def __init__(self):
        self.model = "claude-opus-4-5-20251101"
    
    async def verify(self, reply_text: str, message_context: str) -> VerificationOutput:
        """Verify that reply meets L'Oréal brand standards"""
        try:
            prompt = f"""Review this customer service reply for L'Oréal brand compliance.

Customer message: "{message_context}"
Proposed reply: "{reply_text}"

Check for:
1. Accuracy (no false claims about products)
2. Brand tone (professional, helpful, caring)
3. No harmful/discriminatory content
4. No medical claims
5. Appropriate length

Respond with JSON:
{{
  "verdict": "approved|flagged|rejected",
  "issues": ["list of issues if any"],
  "suggestions": "improvement suggestions if any"
}}"""
            
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            response_text = response.content[0].text
            try:
                data = json.loads(response_text)
            except:
                if "```json" in response_text:
                    data = json.loads(response_text.split("```json")[1].split("```")[0])
                else:
                    data = json.loads(response_text.split("```")[1].split("```")[0])
            
            return VerificationOutput(
                verdict=data.get("verdict", "approved"),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", "")
            )
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            # Safe fallback
            return VerificationOutput(
                verdict="flagged",
                issues=[f"Error verifying: {str(e)}"],
                suggestions="Manual review required"
            )
