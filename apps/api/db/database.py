"""
Database connection et utilitaires
"""

import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from config import settings

logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "timeout": 10,
        "server_settings": {"jit": "off"}
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    """Initialize database tables with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection initialized")
                return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️  Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"❌ Database connection failed after {max_retries} attempts: {e}")
                logger.info("⚠️  Continuing without database - queries will fail gracefully")
    
async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
