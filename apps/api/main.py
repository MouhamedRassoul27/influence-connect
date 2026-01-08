"""
FastAPI Main Application - Influence Connect
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routes import health, messages, influencers, tracking, eval_routes
from db.database import init_db

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Influence Connect API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"HITL Required: {settings.hitl_required}")
    logger.info(f"Models: Classifier={settings.model_classifier}, Drafter={settings.model_drafter}, Verifier={settings.model_verifier}")
    
    # Initialize database
    await init_db()
    
    yield
    
    logger.info("👋 Shutting down Influence Connect API")

app = FastAPI(
    title="Influence Connect API",
    description="IA Community Manager L'Oréal avec HITL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(influencers.router, prefix="/api/influencers", tags=["influencers"])
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(eval_routes.router, prefix="/api/eval", tags=["evaluation"])

@app.get("/")
async def root():
    return {
        "service": "Influence Connect API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api")
async def api_root():
    return {
        "service": "Influence Connect API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "messages": "/api/messages",
            "influencers": "/api/influencers",
            "tracking": "/api/tracking"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
