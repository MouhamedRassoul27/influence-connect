"""
Health check routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db
import anthropic
from config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Anthropic API
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        # Don't actually call API, just check key is set
        anthropic_status = "configured" if settings.anthropic_api_key else "missing_key"
    except Exception as e:
        anthropic_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "database": db_status,
        "anthropic": anthropic_status,
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
