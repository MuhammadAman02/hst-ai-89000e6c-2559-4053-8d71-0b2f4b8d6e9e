from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import asyncio
from typing import Dict, List
import uuid
from datetime import datetime

from app.models.game import WorldState, Block, Player, Position, BlockUpdate, PlayerUpdate
from app.services.world_manager import WorldManager
from app.services.connection_manager import ConnectionManager

app = FastAPI(
    title="Minecraft Clone API",
    description="Backend API for a Minecraft-like voxel world game",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.fly.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
world_manager = WorldManager()
connection_manager = ConnectionManager()

# Serve React build files (for production)
try:
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
except Exception:
    pass  # Frontend build not available in development

@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {
        "message": "Minecraft Clone API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "players_online": len(connection_manager.active_connections),
        "world_blocks": len(world_manager.get_world_state().blocks)
    }

@app.get("/health")
async def health_check():
    """Health check for deployment"""
    return {"status": "healthy"}

@app.get("/api/world")
async def get_world_state():
    """Get current world state"""
    return world_manager.get_world_state()

@app.get("/api/stats")
async def get_game_stats():
    """Get game statistics"""
    return {
        "players_online": len(connection_manager.active_connections),
        "total_blocks": len(world_manager.get_world_state().blocks),
        "uptime": world_manager.get_uptime(),
        "world_size": world_manager.get_world_bounds()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time game communication"""
    player_id = str(uuid.uuid4())
    await connection_manager.connect(websocket, player_id)
    
    try:
        # Send initial world state
        world_state = world_manager.get_world_state()
        await websocket.send_text(json.dumps({
            "type": "world_update",
            "worldState": world_state.dict()
        }))
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "player_joined",
            "playerId": player_id,
            "message": f"Welcome to the world! Player ID: {player_id}"
        }))
        
        # Broadcast player joined to others
        await connection_manager.broadcast_to_others(json.dumps({
            "type": "player_joined",
            "playerId": player_id
        }), player_id)
        
        # Send updated stats
        await connection_manager.broadcast(json.dumps({
            "type": "stats_update",
            "stats": {
                "playersOnline": len(connection_manager.active_connections)
            }
        }))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(message, player_id, websocket)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(player_id)
        
        # Broadcast player left
        await connection_manager.broadcast(json.dumps({
            "type": "player_left",
            "playerId": player_id
        }))
        
        # Send updated stats
        await connection_manager.broadcast(json.dumps({
            "type": "stats_update",
            "stats": {
                "playersOnline": len(connection_manager.active_connections)
            }
        }))
        
        print(f"Player {player_id} disconnected")

async def handle_websocket_message(message: dict, player_id: str, websocket: WebSocket):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "block_update":
        # Handle block placement/destruction
        position = Position(**message["position"])
        block_type = message["blockType"]
        
        # Update world state
        success = world_manager.update_block(position, block_type)
        
        if success:
            # Broadcast block update to all clients
            await connection_manager.broadcast(json.dumps({
                "type": "block_update",
                "position": position.dict(),
                "blockType": block_type,
                "playerId": player_id
            }))
    
    elif message_type == "player_update":
        # Handle player position/rotation update
        position = Position(**message["position"])
        rotation = Position(**message["rotation"])
        
        # Update player state
        world_manager.update_player(player_id, position, rotation)
        
        # Broadcast player update to other clients
        await connection_manager.broadcast_to_others(json.dumps({
            "type": "player_update",
            "playerId": player_id,
            "position": position.dict(),
            "rotation": rotation.dict()
        }), player_id)
    
    elif message_type == "chat_message":
        # Handle chat messages
        chat_message = message.get("message", "")
        
        # Broadcast chat message to all clients
        await connection_manager.broadcast(json.dumps({
            "type": "chat_message",
            "playerId": player_id,
            "message": chat_message,
            "timestamp": datetime.now().isoformat()
        }))
    
    else:
        print(f"Unknown message type: {message_type}")

# Serve React app for any unmatched routes (SPA routing)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for client-side routing"""
    try:
        return FileResponse("frontend/build/index.html")
    except Exception:
        return {"message": "Frontend not available in development mode"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)