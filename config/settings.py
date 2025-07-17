from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "CV Maker Inteligente"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite:///./cvmaker.db"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Storage
    pdf_storage_path: str = "./storage/pdfs"
    log_storage_path: str = "./storage/logs"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # NLP Configuration
    spacy_model: str = "pt_core_news_sm"  # Portuguese model
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    # CORS Configuration
    allowed_origins: list = ["http://localhost:8501", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
