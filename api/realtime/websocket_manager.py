import json
from fastapi import WebSocket
from typing import Dict, List, Optional

class ConnectionManager:
    def __init__(self):
        
        self.active_connections: Dict[str, WebSocket] = {}
        
        self.user_rooms: Dict[str, str] = {}
        
        self.room_connections: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, room_id: Optional[str] = None):
        await websocket.accept()
        
        self.active_connections[client_id] = websocket
        
        
        if room_id:
            await self.join_room(client_id, room_id)
        
        
        await self.send_personal_message(
            client_id, 
            {"type": "connection_success", "message": "Connected to WebSocket server"}
        )
    
    def disconnect(self, client_id: str):
        
        if client_id in self.user_rooms:
            room_id = self.user_rooms[client_id]
            if room_id in self.room_connections:
                self.room_connections[room_id].remove(client_id)
            del self.user_rooms[client_id]
        
        
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, client_id: str, message: Dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: Dict, exclude_client_id: Optional[str] = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client_id:
                await connection.send_text(json.dumps(message))
    
    async def join_room(self, client_id: str, room_id: str):
        
        if client_id in self.user_rooms:
            await self.leave_room(client_id)
        
        
        self.user_rooms[client_id] = room_id
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        if client_id not in self.room_connections[room_id]:
            self.room_connections[room_id].append(client_id)
        
        
        await self.send_room_message(
            room_id, 
            {"type": "user_joined", "client_id": client_id}, 
            exclude_client_id=client_id
        )
    
    async def leave_room(self, client_id: str):
        if client_id not in self.user_rooms:
            return
        
        room_id = self.user_rooms[client_id]
        if room_id in self.room_connections:
            self.room_connections[room_id].remove(client_id)
            
            
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
        
        del self.user_rooms[client_id]
        
        
        await self.send_room_message(
            room_id, 
            {"type": "user_left", "client_id": client_id}
        )
    
    async def send_room_message(self, room_id: str, message: Dict, exclude_client_id: Optional[str] = None):
        if room_id not in self.room_connections:
            return
        
        for client_id in self.room_connections[room_id]:
            if client_id != exclude_client_id:
                await self.send_personal_message(client_id, message)

manager = ConnectionManager()
