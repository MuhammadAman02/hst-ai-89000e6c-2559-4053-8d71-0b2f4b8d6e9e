from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # World settings
    world_size: int = 100
    max_height: int = 50
    auto_save_interval: int = 300  # seconds
    
    # Player settings
    max_players: int = 50
    player_timeout: int = 300  # seconds
    
    # Performance settings
    max_blocks_per_update: int = 100
    broadcast_rate_limit: float = 0.1  # seconds between broadcasts
    
    # Security settings
    cors_origins: list = ["http://localhost:3000", "https://*.fly.dev"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()