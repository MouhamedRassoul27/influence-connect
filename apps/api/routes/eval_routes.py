"""
Routes evaluation - Métriques qualité IA
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from db.database import get_db

router = APIRouter()

@router.get("/metrics")
async def get_eval_metrics(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get evaluation metrics for AI quality"""
    
    # Approval rates
    result = await db.execute(
        text("""
            SELECT 
                action,
                COUNT(*) as count
            FROM approvals
            WHERE created_at >= NOW() - INTERVAL ':days days'
            GROUP BY action
        """),
        {"days": days}
    )
    
    approval_stats = {row.action: row.count for row in result}
    total_approvals = sum(approval_stats.values())
    
    approval_rate = approval_stats.get('approved', 0) / total_approvals if total_approvals > 0 else 0
    edit_rate = approval_stats.get('edited', 0) / total_approvals if total_approvals > 0 else 0
    escalate_rate = approval_stats.get('escalated', 0) / total_approvals if total_approvals > 0 else 0
    
    # Top intents
    result = await db.execute(
        text("""
            SELECT intent, COUNT(*) as count
            FROM drafts
            WHERE created_at >= NOW() - INTERVAL ':days days'
            GROUP BY intent
            ORDER BY count DESC
            LIMIT 10
        """),
        {"days": days}
    )
    
    top_intents = [{"intent": row.intent, "count": row.count} for row in result]
    
    # Top risks
    result = await db.execute(
        text("""
            SELECT risk_level, COUNT(*) as count
            FROM drafts
            WHERE created_at >= NOW() - INTERVAL ':days days'
            GROUP BY risk_level
        """),
        {"days": days}
    )
    
    risk_distribution = {row.risk_level: row.count for row in result}
    
    # Average confidence
    result = await db.execute(
        text("""
            SELECT AVG(intent_confidence) as avg_confidence
            FROM drafts
            WHERE created_at >= NOW() - INTERVAL ':days days'
        """),
        {"days": days}
    )
    
    avg_confidence = result.scalar_one()
    
    return {
        "period_days": days,
        "total_processed": total_approvals,
        "approval_rate": round(approval_rate, 3),
        "edit_rate": round(edit_rate, 3),
        "escalate_rate": round(escalate_rate, 3),
        "avg_confidence": round(avg_confidence, 3) if avg_confidence else 0,
        "top_intents": top_intents,
        "risk_distribution": risk_distribution
    }

@router.get("/logs")
async def get_logs(
    log_type: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get processing logs for debugging"""
    
    where_clause = ""
    params = {"limit": limit}
    
    if log_type:
        where_clause = "WHERE log_type = :log_type"
        params["log_type"] = log_type
    
    result = await db.execute(
        text(f"""
            SELECT * FROM logs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        params
    )
    
    logs = [dict(row._mapping) for row in result]
    return {"logs": logs, "count": len(logs)}
