"""
Service de draft - Génération réponse (Claude Sonnet)
"""

import json
import logging
import anthropic
from typing import List

from config import settings
from models.schemas import DraftOutput, RAGExtract, ClassificationOutput
from prompts.system_prompts import SYSTEM_DRAFTER

logger = logging.getLogger(__name__)

class DrafterService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_drafter
        
    async def draft(
        self,
        message: str,
        classification: ClassificationOutput,
        rag_extracts: List[RAGExtract],
        context: dict = None
    ) -> DraftOutput:
        """
        Generate draft reply avec Claude Sonnet
        """
        try:
            # Construct user prompt
            user_prompt = f"""Message utilisateur:
{message}

Intent détecté: {classification.intent}
Confiance: {classification.intent_confidence:.2f}
Risk level: {classification.risk_level}
Langue: {classification.language}
"""

            # Add RAG context
            if rag_extracts:
                user_prompt += "\n\nSources knowledge base (utilise ces informations):\n"
                for i, extract in enumerate(rag_extracts, 1):
                    user_prompt += f"\n{i}. [{extract.doc_type}] {extract.title}\n"
                    user_prompt += f"   {extract.content}\n"
                    user_prompt += f"   (doc_id={extract.doc_id}, similarity={extract.similarity_score:.2f})\n"
            
            # Add context if thread
            if context:
                user_prompt += f"\n\nContexte conversation: {json.dumps(context, ensure_ascii=False)}\n"
            
            user_prompt += "\n\nGénère la réponse au format JSON strict comme spécifié."
            
            # Call Claude Sonnet
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.8,
                system=SYSTEM_DRAFTER,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Parse JSON
            content = response.content[0].text
            logger.debug(f"Drafter raw response: {content[:200]}...")
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            result_dict = json.loads(content)
            
            # Validate with Pydantic
            draft = DraftOutput(**result_dict)
            
            logger.info(f"✅ Draft generated: {len(draft.reply_text)} chars, {len(draft.suggested_products)} products, confidence={draft.confidence:.2f}")
            
            return draft
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in drafter: {str(e)}")
            logger.error(f"Raw content: {content}")
            # Fallback generic response
            return DraftOutput(
                reply_text="Merci pour votre message. Nous allons revenir vers vous rapidement avec une réponse personnalisée.",
                confidence=0.3
            )
            
        except Exception as e:
            logger.error(f"❌ Drafter error: {str(e)}")
            raise
