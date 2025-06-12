from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Position(BaseModel):
    """3D position coordinates"""
    x: float
    y: float
    z: float

class Block(BaseModel):
    """Block in the world"""
    position: Position
    type: int = Field(..., ge=0, le=10, description="Block type ID")
    placed_by: Optional[str] = None
    placed_at: Optional[datetime] = None

class Player(BaseModel):
    """Player in the world"""
    id: str
    position: Position
    rotation: Position
    connected_at: datetime
    last_active: datetime

class WorldState(BaseModel):
    """Complete world state"""
    blocks: List[Block] = []
    players: List[Player] = []
    world_size: Dict[str, int] = {"width": 100, "height": 50, "depth": 100}
    created_at: datetime
    last_modified: datetime

class BlockUpdate(BaseModel):
    """Block update message"""
    position: Position
    block_type: int = Field(..., ge=0, le=10)
    player_id: str

class PlayerUpdate(BaseModel):
    """Player update message"""
    player_id: str
    position: Position
    rotation: Position

class ChatMessage(BaseModel):
    """Chat message"""
    player_id: str
    message: str = Field(..., max_length=500)
    timestamp: datetime

class GameStats(BaseModel):
    """Game statistics"""
    players_online: int
    total_blocks: int
    blocks_placed_today: int
    blocks_destroyed_today: int
    uptime_seconds: int
    world_bounds: Dict[str, int]