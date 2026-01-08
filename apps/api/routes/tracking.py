"""
Routes tracking - Attribution UTM + events
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import logging

from db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

class TrackingEvent(BaseModel):
    event_type: str  # 'click', 'view_content', 'add_to_cart', 'purchase'
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None  # influencer_id
    influencer_id: Optional[int] = None
    promo_code: Optional[str] = None
    product_id: Optional[str] = None
    value: Optional[float] = None
    currency: str = "EUR"
    metadata: dict = {}

@router.post("/event")
async def track_event(
    event: TrackingEvent,
    db: AsyncSession = Depends(get_db)
):
    """Track attribution event"""
    try:
        await db.execute(
            text("""
                INSERT INTO tracking_events (
                    event_type, user_id, session_id, utm_source, utm_medium,
                    utm_campaign, utm_content, influencer_id, promo_code,
                    product_id, value, currency, metadata
                )
                VALUES (
                    :event_type, :user_id, :session_id, :utm_source, :utm_medium,
                    :utm_campaign, :utm_content, :influencer_id, :promo_code,
                    :product_id, :value, :currency, :metadata
                )
            """),
            event.dict()
        )
        await db.commit()
        
        logger.info(f"📊 Tracked event: {event.event_type} from {event.utm_source}/{event.utm_medium}")
        
        return {"status": "success", "event": event.event_type}
        
    except Exception as e:
        logger.error(f"❌ Tracking error: {str(e)}")
        await db.rollback()
        return {"status": "error", "message": str(e)}

@router.get("/stats")
async def get_tracking_stats(
    influencer_id: Optional[int] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get tracking statistics"""
    
    where_clause = "WHERE created_at >= NOW() - INTERVAL ':days days'"
    params = {"days": days}
    
    if influencer_id:
        where_clause += " AND influencer_id = :influencer_id"
        params["influencer_id"] = influencer_id
    
    # Events by type
    result = await db.execute(
        text(f"""
            SELECT event_type, COUNT(*) as count, SUM(value) as total_value
            FROM tracking_events
            {where_clause}
            GROUP BY event_type
        """),
        params
    )
    
    events_by_type = {row.event_type: {"count": row.count, "value": row.total_value} for row in result}
    
    # Top influencers
    result = await db.execute(
        text(f"""
            SELECT influencer_id, COUNT(*) as events, SUM(value) as total_value
            FROM tracking_events
            {where_clause} AND influencer_id IS NOT NULL
            GROUP BY influencer_id
            ORDER BY total_value DESC
            LIMIT 10
        """),
        params
    )
    
    top_influencers = [{"influencer_id": row.influencer_id, "events": row.events, "value": row.total_value} for row in result]
    
    return {
        "period_days": days,
        "events_by_type": events_by_type,
        "top_influencers": top_influencers
    }
