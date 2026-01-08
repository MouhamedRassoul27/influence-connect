"""
Database connection et utilitaires
"""

import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from config import settings
from models.orm import Base

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

async def init_db():
    """Initialize database tables with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"📊 Database init attempt {attempt + 1}/{max_retries}...")
            
            # Create pgvector extension first
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    logger.info("✅ pgvector extension loaded")
                except Exception as e:
                    logger.warning(f"⚠️  pgvector not available: {e}")
            
            # Create all tables from ORM models
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ All database tables created successfully")
            
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️  Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"❌ Database initialization failed after {max_retries} attempts: {e}")
                raise
    
async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
