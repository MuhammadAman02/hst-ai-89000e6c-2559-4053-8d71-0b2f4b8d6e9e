from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_connections: Dict[str, str] = {}  # player_id -> connection_id
    
    async def connect(self, websocket: WebSocket, player_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[player_id] = websocket
        self.player_connections[player_id] = player_id
        print(f"Player {player_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, player_id: str):
        """Remove a WebSocket connection"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]
        if player_id in self.player_connections:
            del self.player_connections[player_id]
        print(f"Player {player_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, player_id: str):
        """Send a message to a specific player"""
        if player_id in self.active_connections:
            websocket = self.active_connections[player_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Failed to send message to {player_id}: {e}")
                self.disconnect(player_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected players"""
        if not self.active_connections:
            return
        
        disconnected_players = []
        
        for player_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Failed to broadcast to {player_id}: {e}")
                disconnected_players.append(player_id)
        
        # Clean up disconnected players
        for player_id in disconnected_players:
            self.disconnect(player_id)
    
    async def broadcast_to_others(self, message: str, exclude_player_id: str):
        """Broadcast a message to all players except one"""
        if not self.active_connections:
            return
        
        disconnected_players = []
        
        for player_id, websocket in self.active_connections.items():
            if player_id == exclude_player_id:
                continue
            
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Failed to broadcast to {player_id}: {e}")
                disconnected_players.append(player_id)
        
        # Clean up disconnected players
        for player_id in disconnected_players:
            self.disconnect(player_id)
    
    async def broadcast_to_area(self, message: str, center_x: float, center_z: float, radius: float = 50.0):
        """Broadcast a message to players within a certain area"""
        # This would require player position tracking
        # For now, just broadcast to all
        await self.broadcast(message)
    
    def get_connected_players(self) -> List[str]:
        """Get list of connected player IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    async def ping_all(self):
        """Send ping to all connections to check if they're alive"""
        if not self.active_connections:
            return
        
        ping_message = json.dumps({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
        await self.broadcast(ping_message)