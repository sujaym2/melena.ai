from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Melena.ai Healthcare API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://melena_user:melena_password@localhost:5432/melena_healthcare"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # External APIs
    CMS_API_KEY: Optional[str] = None
    GOODRX_API_KEY: Optional[str] = None
    
    # Illinois Healthcare Data Sources
    ILLINOIS_DEPARTMENT_OF_PUBLIC_HEALTH_URL: str = "https://dph.illinois.gov"
    ILLINOIS_HOSPITAL_ASSOCIATION_URL: str = "https://www.iha.org"
    
    # Chicago Hospitals (Phase 1 targets)
    CHICAGO_HOSPITALS: List[str] = [
        "Northwestern Memorial Hospital",
        "Rush University Medical Center", 
        "University of Chicago Medical Center",
        "Advocate Christ Medical Center",
        "Loyola University Medical Center",
        "Swedish Covenant Hospital",
        "Presence Saint Joseph Hospital",
        "Mercy Hospital & Medical Center"
    ]
    
    # Data Processing
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FILE_TYPES: List[str] = [".csv", ".xlsx", ".xls", ".json"]
    
    # ML Model Settings
    MODEL_UPDATE_FREQUENCY_HOURS: int = 24
    PRICE_ANOMALY_THRESHOLD: float = 2.0  # 2x standard deviation
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Override with environment variables if present
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("REDIS_URL"):
    settings.REDIS_URL = os.getenv("REDIS_URL")
if os.getenv("SECRET_KEY"):
    settings.SECRET_KEY = os.getenv("SECRET_KEY")
