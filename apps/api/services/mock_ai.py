"""
Mock services for testing without Anthropic API (free)
"""

from models.schemas import ClassificationOutput, DraftOutput, VerificationOutput, RAGExtract, Issue, IssueSeverity, IssueType

class MockClassifierService:
    def __init__(self):
        self.model = "claude-haiku-4-5-20251001-MOCK"
    
    async def classify(self, message: str, context=None):
        """Mock classification"""
        return ClassificationOutput(
            intent="recommendation",
            intent_confidence=0.92,
            risk_flags=[],
            risk_level="low",
            language="fr",
            should_dm=False,
            should_escalate=False,
            reasoning="Mock classification - message suggests product recommendation"
        )

class MockDrafterService:
    def __init__(self):
        self.model = "claude-sonnet-4-5-20250929-MOCK"
    
    async def draft(self, message: str, classification, rag_extracts, context=None):
        """Mock draft generation"""
        return DraftOutput(
            reply_text="Merci pour votre question ! Pour une peau grasse, je vous recommande notre gel purifiant léger qui régule l'excès de sébum. Avez-vous des préoccupations spécifiques ?",
            ask_dm_question="Quelle est votre type de peau exactement ?",
            suggested_products=[
                {
                    "name": "Pure Zone Gel Purifiant",
                    "category": "Soin visage",
                    "price": "18.99 EUR",
                    "reason": "Formule légère pour peau grasse"
                }
            ],
            suggested_influencers=["influencer_1", "influencer_2"],
            citations_internal=[],
            confidence=0.85
        )

class MockVerifierService:
    def __init__(self):
        self.model = "claude-opus-4-5-20251101-MOCK"
    
    async def verify(self, draft, classification, original_message):
        """Mock verification"""
        return VerificationOutput(
            verdict="PASS",
            issues=[],
            reasoning="Mock verification - reply is brand-safe and compliant"
        )
