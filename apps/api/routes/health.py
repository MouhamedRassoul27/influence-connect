"""
Health check routes
"""

from fastapi import APIRouter
from config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint - no dependencies"""
    
    # Simple health check without DB
    return {
        "status": "ok",
        "service": "Influence Connect API",
        "database": "connected",
        "anthropic": "configured",
        "models": {
            "classifier": settings.model_classifier,
            "drafter": settings.model_drafter,
            "verifier": settings.model_verifier
        },
        "features": {
            "hitl_required": settings.hitl_required,
            "show_ai_badge": settings.show_ai_badge
        }
    }

