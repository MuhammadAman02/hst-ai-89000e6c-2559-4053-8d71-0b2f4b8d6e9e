from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Game configuration
    world_size: int = 100
    max_players: int = 50
    auto_save_interval: int = 300  # seconds
    
    # Database configuration
    database_url: str = "sqlite:///./minecraft_clone.db"
    
    # Security
    secret_key: str = "minecraft-clone-secret-key-change-in-production"
    
    # CORS
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()