"""
Service de classification - Intent + Risk (Claude Haiku)
"""

import json
import logging
import anthropic
from typing import Dict

from config import settings
from models.schemas import ClassificationOutput
from prompts.system_prompts import SYSTEM_CLASSIFIER

logger = logging.getLogger(__name__)

class ClassifierService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_classifier
        
    async def classify(self, message: str, context: Dict = None) -> ClassificationOutput:
        """
        Classify intent + risk pour un message
        Returns ClassificationOutput (validated by Pydantic)
        """
        try:
            # Construct user prompt with context
            user_prompt = f"Message à classifier:\n\n{message}"
            
            if context:
                user_prompt += f"\n\nContexte additionnel: {json.dumps(context, ensure_ascii=False)}"
            
            # Call Claude Haiku
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                system=SYSTEM_CLASSIFIER,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Parse JSON response
            content = response.content[0].text
            logger.debug(f"Classifier raw response: {content}")
            
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result_dict = json.loads(content)
            
            # Validate with Pydantic
            classification = ClassificationOutput(**result_dict)
            
            logger.info(f"✅ Classified: intent={classification.intent} ({classification.intent_confidence:.2f}), risk={classification.risk_level}, flags={classification.risk_flags}")
            
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in classifier: {str(e)}")
            logger.error(f"Raw content: {content}")
            # Fallback
            return ClassificationOutput(
                intent="unknown",
                intent_confidence=0.5,
                risk_flags=[],
                risk_level="medium",
                should_escalate=True,
                reasoning=f"Parse error: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"❌ Classifier error: {str(e)}")
            raise
