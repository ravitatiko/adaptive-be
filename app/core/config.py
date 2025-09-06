from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Adaptive Learning Platform"
    version: str = "1.0.0"
    description: str = "A modern adaptive learning platform with FastAPI backend and React frontend"
    
    # LLM Configuration
    google_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_provider: str = "google"
    default_llm_model: str = "gemini-1.5-flash"
    max_tokens_default: int = 1000
    temperature_default: float = 0.7
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fallback to environment variable if not set in .env
        if not self.google_api_key:
            self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
