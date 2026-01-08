"""
Service RAG - Retrieval Augmented Generation avec pgvector (MOCK pour tests)
"""

import logging
from typing import List

from models.schemas import RAGExtract

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_model_name = "BAAI/bge-m3-MOCK"
        logger.info(f"RAG Service initialized (MOCK - no embeddings)")
    
    def embed(self, text: str) -> List[float]:
        """Mock embedding - returns zeros"""
        return [0.0] * 1024
        
    async def retrieve(
        self, 
        query: str, 
        db,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[RAGExtract]:
        """Mock retrieve - returns empty list"""
        logger.info(f"RAG retrieve (mock): query='{query[:30]}...'")
        return []
            
    async def ingest_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        category: str,
        db,
        source_file: str = None,
        metadata: dict = None
    ) -> int:
        """Mock ingest - returns fake ID"""
        logger.info(f"RAG ingest (mock): {title}")
        return 1

