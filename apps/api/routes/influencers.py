"""
Routes influencers - CRUD ambassadeurs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
import json

from db.database import get_db
from models.schemas import Influencer, InfluencerTags

router = APIRouter()

@router.get("/", response_model=List[Influencer])
async def list_influencers(
    status: str = "active",
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all influencers"""
    result = await db.execute(
        text("""
            SELECT * FROM influencers
            WHERE status = :status
            ORDER BY name
            LIMIT :limit
        """),
        {"status": status, "limit": limit}
    )
    
    influencers = []
    for row in result:
        influencers.append(Influencer(
            id=row.id,
            name=row.name,
            instagram_handle=row.instagram_handle,
            tiktok_handle=row.tiktok_handle,
            email=row.email,
            tags=InfluencerTags(**row.tags),
            promo_code=row.promo_code,
            commission_rate=row.commission_rate,
            status=row.status
        ))
    
    return influencers

@router.post("/", response_model=Influencer)
async def create_influencer(
    influencer: Influencer,
    db: AsyncSession = Depends(get_db)
):
    """Create new influencer"""
    result = await db.execute(
        text("""
            INSERT INTO influencers (name, instagram_handle, tiktok_handle, email, tags, promo_code, commission_rate, status)
            VALUES (:name, :instagram_handle, :tiktok_handle, :email, :tags, :promo_code, :commission_rate, :status)
            RETURNING id
        """),
        {
            "name": influencer.name,
            "instagram_handle": influencer.instagram_handle,
            "tiktok_handle": influencer.tiktok_handle,
            "email": influencer.email,
            "tags": json.dumps(influencer.tags.dict()),
            "promo_code": influencer.promo_code,
            "commission_rate": influencer.commission_rate,
            "status": influencer.status
        }
    )
    await db.commit()
    
    influencer.id = result.scalar_one()
    return influencer

@router.get("/{influencer_id}", response_model=Influencer)
async def get_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get influencer by ID"""
    result = await db.execute(
        text("SELECT * FROM influencers WHERE id = :id"),
        {"id": influencer_id}
    )
    
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Influencer not found")
    
    return Influencer(
        id=row.id,
        name=row.name,
        instagram_handle=row.instagram_handle,
        tiktok_handle=row.tiktok_handle,
        email=row.email,
        tags=InfluencerTags(**row.tags),
        promo_code=row.promo_code,
        commission_rate=row.commission_rate,
        status=row.status
    )

@router.put("/{influencer_id}", response_model=Influencer)
async def update_influencer(
    influencer_id: int,
    influencer: Influencer,
    db: AsyncSession = Depends(get_db)
):
    """Update influencer"""
    await db.execute(
        text("""
            UPDATE influencers
            SET name = :name, instagram_handle = :instagram_handle, tiktok_handle = :tiktok_handle,
                email = :email, tags = :tags, promo_code = :promo_code, commission_rate = :commission_rate, status = :status
            WHERE id = :id
        """),
        {
            "id": influencer_id,
            "name": influencer.name,
            "instagram_handle": influencer.instagram_handle,
            "tiktok_handle": influencer.tiktok_handle,
            "email": influencer.email,
            "tags": json.dumps(influencer.tags.dict()),
            "promo_code": influencer.promo_code,
            "commission_rate": influencer.commission_rate,
            "status": influencer.status
        }
    )
    await db.commit()
    
    influencer.id = influencer_id
    return influencer
