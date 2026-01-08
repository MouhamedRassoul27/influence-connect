"""
Service de vérification - Brand-safe check (Claude Opus)
"""

import json
import logging
import anthropic

from config import settings
from models.schemas import VerificationOutput, DraftOutput, ClassificationOutput
from prompts.system_prompts import SYSTEM_VERIFIER

logger = logging.getLogger(__name__)

class VerifierService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_verifier
        
    async def verify(
        self,
        draft: DraftOutput,
        classification: ClassificationOutput,
        original_message: str
    ) -> VerificationOutput:
        """
        Verify draft reply for brand safety and compliance
        """
        try:
            # Construct verification prompt
            user_prompt = f"""Message original utilisateur:
{original_message}

Intent: {classification.intent}
Risk level: {classification.risk_level}
Risk flags: {classification.risk_flags}

Réponse draft à vérifier:
{draft.reply_text}
"""

            if draft.ask_dm_question:
                user_prompt += f"\nQuestion DM suggérée: {draft.ask_dm_question}"
                
            if draft.suggested_products:
                user_prompt += f"\n\nProduits suggérés: {len(draft.suggested_products)}"
                for product in draft.suggested_products:
                    user_prompt += f"\n- {product.name} ({product.price}): {product.reason}"
            
            user_prompt += "\n\nVérifie la conformité et retourne le verdict JSON."
            
            # Call Claude Opus
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.5,
                system=SYSTEM_VERIFIER,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Parse JSON
            content = response.content[0].text
            logger.debug(f"Verifier raw response: {content[:200]}...")
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            result_dict = json.loads(content)
            
            # Validate with Pydantic
            verification = VerificationOutput(**result_dict)
            
            logger.info(f"✅ Verification: {verification.verdict}, {len(verification.issues)} issues")
            if verification.issues:
                for issue in verification.issues:
                    logger.info(f"   - {issue.severity} {issue.type}: {issue.description}")
            
            return verification
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in verifier: {str(e)}")
            logger.error(f"Raw content: {content}")
            # Fallback: escalate si pas de parse
            return VerificationOutput(
                verdict="ESCALATE",
                reasoning=f"Verification parse error: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"❌ Verifier error: {str(e)}")
            raise
