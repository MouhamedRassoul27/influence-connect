"""
Ingestion knowledge base depuis seed_db.py
Génère embeddings avec BAAI/bge-m3 + pgvector
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import numpy as np

# Import KNOWLEDGE_DOCS from seed
from seed_db import KNOWLEDGE_DOCS

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://influence:influence123@localhost:5432/influenceconnect")
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Embedding model
print("📦 Loading embedding model BAAI/bge-m3...")
model = SentenceTransformer("BAAI/bge-m3")
print("✅ Model loaded")

def embed_text(text: str) -> list[float]:
    """Generate embedding for text"""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

async def ingest_knowledge():
    """Ingest knowledge docs with embeddings"""
    
    print(f"\n🧠 Ingesting {len(KNOWLEDGE_DOCS)} knowledge documents...")
    
    async with AsyncSessionLocal() as db:
        try:
            for i, doc in enumerate(KNOWLEDGE_DOCS, 1):
                # Generate embedding
                embedding = embed_text(doc["content"])
                
                # Insert into knowledge_docs
                await db.execute(
                    text("""
                        INSERT INTO knowledge_docs (title, content, doc_type, category, embedding, created_at)
                        VALUES (:title, :content, :doc_type, :category, :embedding, NOW())
                    """),
                    {
                        "title": doc["title"],
                        "content": doc["content"],
                        "doc_type": doc["doc_type"],
                        "category": doc["category"],
                        "embedding": embedding
                    }
                )
                
                print(f"✅ [{i}/{len(KNOWLEDGE_DOCS)}] {doc['title']}")
            
            await db.commit()
            print(f"\n✅ Ingested {len(KNOWLEDGE_DOCS)} documents successfully!")
            
            # Test query
            print("\n🔍 Testing RAG retrieval...")
            test_query = "J'ai une allergie avec votre produit"
            test_embedding = embed_text(test_query)
            
            result = await db.execute(
                text("""
                    SELECT title, content, 1 - (embedding <=> :query_embedding) AS similarity
                    FROM knowledge_docs
                    WHERE 1 - (embedding <=> :query_embedding) > 0.7
                    ORDER BY similarity DESC
                    LIMIT 3
                """),
                {"query_embedding": test_embedding}
            )
            
            rows = result.fetchall()
            print(f"\nQuery: '{test_query}'")
            print("Top 3 results:")
            for row in rows:
                print(f"  - {row[0]} (similarity: {row[2]:.3f})")
                print(f"    {row[1][:100]}...")
            
        except Exception as e:
            print(f"\n❌ Error ingesting knowledge: {str(e)}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(ingest_knowledge())
