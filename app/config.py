"""
Configuration de l'application
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Database
    database_url: str
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    
    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_version: str = "v1"
    debug: bool = True
    api_secret_key: str
    
    # Sécurité
    max_auth_attempts: int = 3
    session_timeout_minutes: int = 30
    
    # Logs
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Récupère les paramètres de l'application (singleton)"""
    return Settings()
