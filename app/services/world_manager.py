import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from collections import defaultdict

from app.models.game import WorldState, Block, Player, Position

class WorldManager:
    """Manages the game world state and operations"""
    
    def __init__(self):
        self.world_state = WorldState(
            blocks=[],
            players=[],
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        self.players: Dict[str, Player] = {}
        self.blocks: Dict[str, Block] = {}  # Key: "x,y,z"
        self.world_bounds = {"min_x": -50, "max_x": 50, "min_y": 0, "max_y": 50, "min_z": -50, "max_z": 50}
        self.stats = {
            "blocks_placed_today": 0,
            "blocks_destroyed_today": 0,
            "total_operations": 0
        }
        
        # Initialize with some default terrain
        self.generate_initial_terrain()
        
        # Auto-save every 5 minutes
        asyncio.create_task(self.auto_save_loop())
    
    def generate_initial_terrain(self):
        """Generate initial terrain for the world"""
        print("Generating initial terrain...")
        
        # Generate a simple flat world with some hills
        for x in range(-20, 21):
            for z in range(-20, 21):
                # Create height variation
                height = max(0, int(5 + 3 * (0.5 - abs(x/20)) + 2 * (0.5 - abs(z/20))))
                
                for y in range(height + 1):
                    block_type = 3  # Stone
                    
                    if y == height and height > 2:
                        block_type = 1  # Grass on top
                    elif y == height and height <= 2:
                        block_type = 6  # Sand near water
                    elif y >= height - 2 and height > 2:
                        block_type = 2  # Dirt below grass
                    
                    position = Position(x=x, y=y, z=z)
                    self.place_block(position, block_type, system_placed=True)
        
        # Add some trees
        tree_positions = [(5, 5), (-8, 3), (12, -7), (-15, -12), (8, -15)]
        for x, z in tree_positions:
            self.generate_tree(x, z)
        
        print(f"Generated {len(self.blocks)} initial blocks")
    
    def generate_tree(self, x: int, z: int):
        """Generate a tree at the specified position"""
        ground_height = self.get_ground_height(x, z)
        
        if ground_height > 3:  # Only place trees on grass
            # Tree trunk
            for y in range(ground_height + 1, ground_height + 5):
                position = Position(x=x, y=y, z=z)
                self.place_block(position, 5, system_placed=True)  # Wood
            
            # Tree leaves
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    for dy in range(3, 7):
                        if abs(dx) + abs(dz) + abs(dy - 4) <= 3:
                            if not (dx == 0 and dz == 0 and dy <= 4):
                                position = Position(x=x+dx, y=ground_height+dy, z=z+dz)
                                self.place_block(position, 1, system_placed=True)  # Grass/leaves
    
    def get_ground_height(self, x: int, z: int) -> int:
        """Get the height of the ground at the specified x, z coordinates"""
        for y in range(20, -1, -1):
            key = f"{x},{y},{z}"
            if key in self.blocks:
                return y
        return 0
    
    def position_to_key(self, position: Position) -> str:
        """Convert position to string key"""
        return f"{int(position.x)},{int(position.y)},{int(position.z)}"
    
    def is_valid_position(self, position: Position) -> bool:
        """Check if position is within world bounds"""
        return (
            self.world_bounds["min_x"] <= position.x <= self.world_bounds["max_x"] and
            self.world_bounds["min_y"] <= position.y <= self.world_bounds["max_y"] and
            self.world_bounds["min_z"] <= position.z <= self.world_bounds["max_z"]
        )
    
    def place_block(self, position: Position, block_type: int, player_id: Optional[str] = None, system_placed: bool = False) -> bool:
        """Place a block at the specified position"""
        if not self.is_valid_position(position):
            return False
        
        key = self.position_to_key(position)
        
        # Remove existing block if present
        if key in self.blocks:
            del self.blocks[key]
        
        # Place new block (if not air)
        if block_type > 0:
            block = Block(
                position=position,
                type=block_type,
                placed_by=player_id,
                placed_at=datetime.now()
            )
            self.blocks[key] = block
            
            if not system_placed:
                self.stats["blocks_placed_today"] += 1
        else:
            if not system_placed:
                self.stats["blocks_destroyed_today"] += 1
        
        self.world_state.last_modified = datetime.now()
        self.stats["total_operations"] += 1
        
        return True
    
    def update_block(self, position: Position, block_type: int, player_id: Optional[str] = None) -> bool:
        """Update a block (place or remove)"""
        return self.place_block(position, block_type, player_id)
    
    def get_block_at(self, position: Position) -> Optional[Block]:
        """Get block at specified position"""
        key = self.position_to_key(position)
        return self.blocks.get(key)
    
    def update_player(self, player_id: str, position: Position, rotation: Position):
        """Update player position and rotation"""
        if player_id in self.players:
            self.players[player_id].position = position
            self.players[player_id].rotation = rotation
            self.players[player_id].last_active = datetime.now()
        else:
            # Create new player
            self.players[player_id] = Player(
                id=player_id,
                position=position,
                rotation=rotation,
                connected_at=datetime.now(),
                last_active=datetime.now()
            )
    
    def remove_player(self, player_id: str):
        """Remove player from world"""
        if player_id in self.players:
            del self.players[player_id]
    
    def get_world_state(self) -> WorldState:
        """Get current world state"""
        self.world_state.blocks = list(self.blocks.values())
        self.world_state.players = list(self.players.values())
        return self.world_state
    
    def get_uptime(self) -> int:
        """Get server uptime in seconds"""
        return int((datetime.now() - self.world_state.created_at).total_seconds())
    
    def get_world_bounds(self) -> Dict[str, int]:
        """Get world boundaries"""
        return self.world_bounds
    
    def get_stats(self) -> Dict:
        """Get world statistics"""
        return {
            **self.stats,
            "total_blocks": len(self.blocks),
            "active_players": len(self.players),
            "uptime_seconds": self.get_uptime()
        }
    
    async def auto_save_loop(self):
        """Auto-save world state periodically"""
        while True:
            await asyncio.sleep(300)  # Save every 5 minutes
            try:
                await self.save_world()
            except Exception as e:
                print(f"Auto-save failed: {e}")
    
    async def save_world(self):
        """Save world state to file"""
        try:
            world_data = {
                "blocks": [block.dict() for block in self.blocks.values()],
                "stats": self.stats,
                "created_at": self.world_state.created_at.isoformat(),
                "last_modified": datetime.now().isoformat()
            }
            
            os.makedirs("data", exist_ok=True)
            with open("data/world.json", "w") as f:
                json.dump(world_data, f, indent=2)
            
            print(f"World saved: {len(self.blocks)} blocks")
        except Exception as e:
            print(f"Failed to save world: {e}")
    
    async def load_world(self):
        """Load world state from file"""
        try:
            if os.path.exists("data/world.json"):
                with open("data/world.json", "r") as f:
                    world_data = json.load(f)
                
                # Load blocks
                self.blocks = {}
                for block_data in world_data.get("blocks", []):
                    block = Block(**block_data)
                    key = self.position_to_key(block.position)
                    self.blocks[key] = block
                
                # Load stats
                self.stats.update(world_data.get("stats", {}))
                
                print(f"World loaded: {len(self.blocks)} blocks")
        except Exception as e:
            print(f"Failed to load world: {e}")