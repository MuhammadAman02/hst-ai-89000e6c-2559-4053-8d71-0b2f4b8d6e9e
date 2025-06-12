from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import os

from app.models.game import (
    WorldState, Block, Player, Position, BlockUpdate, 
    PlayerUpdate, ChatMessage, GameStats
)
from app.services.connection_manager import ConnectionManager
from app.services.world_manager import WorldManager
from app.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Minecraft Clone API",
    description="Real-time multiplayer voxel world game backend",
    version="1.0.0"
)

# Configuration
settings = get_settings()

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
connection_manager = ConnectionManager()
world_manager = WorldManager()

# Serve static files (React build)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🌍 Initializing Minecraft Clone Server...")
    await world_manager.load_world()
    print("✅ Server initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("💾 Saving world state...")
    await world_manager.save_world()
    print("👋 Server shutdown complete!")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "players_online": connection_manager.get_connection_count(),
        "total_blocks": len(world_manager.blocks),
        "uptime_seconds": world_manager.get_uptime()
    }

# Serve React frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the React frontend"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Minecraft Clone</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #87ceeb 0%, #98fb98 100%);
                font-family: 'Arial', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: #333;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.9);
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                max-width: 600px;
            }
            h1 {
                color: #2c5530;
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }
            .subtitle {
                font-size: 1.2rem;
                color: #666;
                margin-bottom: 2rem;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #4a7c59;
            }
            .feature h3 {
                color: #2c5530;
                margin-bottom: 0.5rem;
            }
            .api-info {
                background: #e8f5e8;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 2rem 0;
            }
            .endpoint {
                background: #fff;
                padding: 0.5rem 1rem;
                margin: 0.5rem 0;
                border-radius: 5px;
                font-family: monospace;
                border-left: 3px solid #4a7c59;
            }
            .status {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 15px;
                font-size: 0.9rem;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Minecraft Clone</h1>
            <div class="status">🟢 Server Online</div>
            <p class="subtitle">Real-time multiplayer voxel world game backend</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🌍 3D Voxel World</h3>
                    <p>Infinite block-based world with terrain generation</p>
                </div>
                <div class="feature">
                    <h3>👥 Multiplayer</h3>
                    <p>Real-time multiplayer with WebSocket communication</p>
                </div>
                <div class="feature">
                    <h3>🏗️ Building System</h3>
                    <p>Place and destroy blocks with multiple block types</p>
                </div>
                <div class="feature">
                    <h3>💾 World Persistence</h3>
                    <p>Automatic world saving and loading</p>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🔌 API Endpoints</h3>
                <div class="endpoint">GET /health - Server health check</div>
                <div class="endpoint">GET /api/world - Get world state</div>
                <div class="endpoint">GET /api/stats - Game statistics</div>
                <div class="endpoint">WS /ws/{player_id} - WebSocket connection</div>
            </div>
            
            <p><strong>Connect your React frontend to:</strong><br>
            <code>ws://localhost:8000/ws/{player_id}</code></p>
        </div>
        
        <script>
            // Simple connection test
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    console.log('🎮 Minecraft Clone Server Status:', data);
                })
                .catch(error => {
                    console.error('❌ Server connection failed:', error);
                });
        </script>
    </body>
    </html>
    """

# REST API Endpoints
@app.get("/api/world", response_model=WorldState)
async def get_world_state():
    """Get current world state"""
    return world_manager.get_world_state()

@app.get("/api/stats", response_model=GameStats)
async def get_game_stats():
    """Get game statistics"""
    stats = world_manager.get_stats()
    return GameStats(
        players_online=connection_manager.get_connection_count(),
        total_blocks=stats["total_blocks"],
        blocks_placed_today=stats["blocks_placed_today"],
        blocks_destroyed_today=stats["blocks_destroyed_today"],
        uptime_seconds=stats["uptime_seconds"],
        world_bounds=world_manager.get_world_bounds()
    )

@app.get("/api/players")
async def get_online_players():
    """Get list of online players"""
    return {
        "players": connection_manager.get_connected_players(),
        "count": connection_manager.get_connection_count()
    }

@app.post("/api/world/reset")
async def reset_world():
    """Reset the world (admin only)"""
    world_manager.blocks.clear()
    world_manager.generate_initial_terrain()
    await world_manager.save_world()
    
    # Notify all players
    await connection_manager.broadcast(json.dumps({
        "type": "world_reset",
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "World reset successfully"}

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """WebSocket endpoint for real-time game communication"""
    await connection_manager.connect(websocket, player_id)
    
    # Send initial world state
    world_state = world_manager.get_world_state()
    await connection_manager.send_personal_message(
        json.dumps({
            "type": "world_state",
            "data": world_state.dict(),
            "timestamp": datetime.now().isoformat()
        }),
        player_id
    )
    
    # Notify other players
    await connection_manager.broadcast_to_others(
        json.dumps({
            "type": "player_joined",
            "player_id": player_id,
            "timestamp": datetime.now().isoformat()
        }),
        player_id
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "block_update":
                # Handle block placement/destruction
                block_update = BlockUpdate(**message["data"])
                
                success = world_manager.update_block(
                    block_update.position,
                    block_update.block_type,
                    player_id
                )
                
                if success:
                    # Broadcast to all players
                    await connection_manager.broadcast(json.dumps({
                        "type": "block_update",
                        "data": block_update.dict(),
                        "timestamp": datetime.now().isoformat()
                    }))
            
            elif message_type == "player_update":
                # Handle player movement
                player_update = PlayerUpdate(**message["data"])
                
                world_manager.update_player(
                    player_id,
                    player_update.position,
                    player_update.rotation
                )
                
                # Broadcast to other players
                await connection_manager.broadcast_to_others(
                    json.dumps({
                        "type": "player_update",
                        "data": player_update.dict(),
                        "timestamp": datetime.now().isoformat()
                    }),
                    player_id
                )
            
            elif message_type == "chat_message":
                # Handle chat messages
                chat_message = ChatMessage(
                    player_id=player_id,
                    message=message["data"]["message"],
                    timestamp=datetime.now()
                )
                
                # Broadcast to all players
                await connection_manager.broadcast(json.dumps({
                    "type": "chat_message",
                    "data": chat_message.dict(),
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif message_type == "ping":
                # Handle ping/pong for connection health
                await connection_manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }),
                    player_id
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(player_id)
        world_manager.remove_player(player_id)
        
        # Notify other players
        await connection_manager.broadcast(json.dumps({
            "type": "player_left",
            "player_id": player_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        print(f"Player {player_id} disconnected")
    
    except Exception as e:
        print(f"WebSocket error for player {player_id}: {e}")
        connection_manager.disconnect(player_id)
        world_manager.remove_player(player_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)