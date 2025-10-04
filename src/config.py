# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # This tells Pydantic to load settings from a file named .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')
    
    # Application
    APP_NAME: str
    DEBUG: bool
    API_KEY: str # Added for security, as per the review
    
    # MCP Server
    MCP_HOST: str
    MCP_PORT: int
    
    # Databases
    POSTGRES_URL: str
    REDIS_URL: str
    NEO4J_URL: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # AI Models (Optional, so we keep the default None)
    OPENAI_API_KEY: Optional[str] = None
    
    # Memory Settings
    SHORT_TERM_MEMORY_SIZE: int
    SHORT_TERM_MEMORY_TTL: int

# This single instance is imported by other parts of the app
settings = Settings()