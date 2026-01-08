"""
Configuration centralisée - charge models.yaml, intents.yaml, risk.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://influence:influence123@db:5432/influenceconnect")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Models (overridable par env)
    model_classifier: str = os.getenv("MODEL_CLASSIFIER", "claude-haiku-4-5-20251001")
    model_drafter: str = os.getenv("MODEL_DRAFTER", "claude-sonnet-4-5-20250929")
    model_verifier: str = os.getenv("MODEL_VERIFIER", "claude-opus-4-5-20251101")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    
    # Features
    hitl_required: bool = os.getenv("HITL_REQUIRED", "true").lower() == "true"
    show_ai_badge: bool = os.getenv("SHOW_AI_BADGE", "false").lower() == "true"
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "fr")
    
    # App
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings()

def load_yaml_config(filename: str) -> Dict:
    """Load YAML config file"""
    config_path = Path(__file__).parent / filename
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Load configs
MODELS_CONFIG = load_yaml_config("models.yaml")
INTENTS_CONFIG = load_yaml_config("intents.yaml")
RISK_CONFIG = load_yaml_config("risk.yaml")

# Extract specific configs
def get_model_config(key: str, default: str = "") -> str:
    """Get model ID from config with env override"""
    env_key = f"MODEL_{key.upper()}"
    return os.getenv(env_key, MODELS_CONFIG.get(key, default))

def get_intents() -> List[Dict]:
    """Get list of intents"""
    return INTENTS_CONFIG.get("intents", [])

def get_safe_autopilot_intents() -> List[str]:
    """Get intents safe for autopilot"""
    return [
        intent["id"] 
        for intent in get_intents() 
        if intent.get("safe_autopilot", False)
    ]

def get_risk_flags() -> List[Dict]:
    """Get list of risk flags"""
    return RISK_CONFIG.get("risk_flags", [])

def get_critical_risk_flags() -> List[str]:
    """Get risk flags that trigger auto-escalation"""
    return [
        flag["id"]
        for flag in get_risk_flags()
        if flag.get("auto_escalate", False)
    ]
