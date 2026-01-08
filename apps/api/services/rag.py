"""
Service RAG - Retrieval Augmented Generation avec pgvector
"""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from config import settings
from models.schemas import RAGExtract

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # Load embedding model lazily
        self.model = None
        self.embedding_model_name = settings.embedding_model
        logger.info(f"RAG Service initialized (model will load on first use: {self.embedding_model_name})")
    
    def _ensure_model_loaded(self):
        """Lazy load the embedding model on first use"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            logger.info("✅ Embedding model loaded")
        
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        self._ensure_model_loaded()
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
        
    async def retrieve(
        self, 
        query: str, 
        db: AsyncSession,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[RAGExtract]:
        """
        Retrieve top-k most similar documents from knowledge base
        """
        try:
            # Generate query embedding
            query_embedding = self.embed(query)
            
            # Convert to string format for pgvector
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Query with cosine similarity
            result = await db.execute(
                text("""
                    SELECT 
                        id,
                        title,
                        content,
                        doc_type,
                        category,
                        1 - (embedding <=> :query_embedding::vector) as similarity
                    FROM knowledge_docs
                    WHERE 1 - (embedding <=> :query_embedding::vector) >= :threshold
                    ORDER BY similarity DESC
                    LIMIT :top_k
                """),
                {
                    "query_embedding": embedding_str,
                    "threshold": similarity_threshold,
                    "top_k": top_k
                }
            )
            
            extracts = []
            for row in result:
                extracts.append(RAGExtract(
                    doc_id=row.id,
                    title=row.title,
                    content=row.content[:500],  # Truncate for context window
                    similarity_score=float(row.similarity),
                    doc_type=row.doc_type,
                    category=row.category
                ))
            
            logger.info(f"✅ Retrieved {len(extracts)} knowledge extracts (threshold={similarity_threshold})")
            for i, ext in enumerate(extracts[:3]):
                logger.debug(f"  {i+1}. {ext.title} (sim={ext.similarity_score:.3f})")
            
            return extracts
            
        except Exception as e:
            logger.error(f"❌ RAG retrieve error: {str(e)}")
            return []
            
    async def ingest_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        category: str,
        db: AsyncSession,
        source_file: str = None,
        metadata: dict = None
    ) -> int:
        """
        Ingest a new document into knowledge base
        """
        try:
            # Generate embedding
            embedding = self.embed(content)
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            
            # Insert
            result = await db.execute(
                text("""
                    INSERT INTO knowledge_docs (title, content, doc_type, category, embedding, source_file, metadata)
                    VALUES (:title, :content, :doc_type, :category, :embedding::vector, :source_file, :metadata)
                    RETURNING id
                """),
                {
                    "title": title,
                    "content": content,
                    "doc_type": doc_type,
                    "category": category,
                    "embedding": embedding_str,
                    "source_file": source_file,
                    "metadata": metadata or {}
                }
            )
            await db.commit()
            
            doc_id = result.scalar_one()
            logger.info(f"✅ Ingested doc {doc_id}: {title}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Ingest error: {str(e)}")
            await db.rollback()
            raise
