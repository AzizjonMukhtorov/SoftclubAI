from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Student Churn Prediction API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    # Database
    DATABASE_URL: str = "postgresql://localhost/crm-softclub"
    
    # Groq API Settings
    GROQ_API_KEY: str = ""  
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  
    
    MODEL_PATH: str = "models/trained/churn_model.json"
    
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
