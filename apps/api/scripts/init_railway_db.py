#!/usr/bin/env python3
"""
Script to initialize Railway PostgreSQL database
Run this after deploying to Railway to create all tables
"""

import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def init_database():
    """Create all tables in Railway PostgreSQL"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    # Convert postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        async_database_url = database_url
    
    print(f"🔗 Connecting to database...")
    print(f"   URL: {database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_async_engine(
            async_database_url,
            echo=True,
            pool_pre_ping=True,
        )
        
        # Read and execute init.sql
        init_sql_path = os.path.join(os.path.dirname(__file__), "../db/init.sql")
        print(f"📄 Reading schema from: {init_sql_path}")
        
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in schema.split(';') if s.strip()]
        
        async with engine.begin() as conn:
            for i, statement in enumerate(statements, 1):
                try:
                    await conn.execute(text(statement))
                    print(f"✅ Statement {i}/{len(statements)}")
                except Exception as e:
                    print(f"⚠️  Statement {i} warning: {e}")
        
        print("\n✅ Database initialization complete!")
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)
