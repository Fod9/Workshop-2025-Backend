from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager():
    def __init__(self):
        self.active_connections: dict[int, List[tuple[WebSocket, str]]] = {}

    async def connect(self, websocket: WebSocket, game_id: int, player_name: str = None):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        
        player_name = player_name or "Unknown Player"
        self.active_connections[game_id].append((websocket, player_name))

    def disconnect(self, websocket: WebSocket):
        for connections in self.active_connections.values():
            for connection_tuple in connections[:]:  # Create copy to avoid modification during iteration
                if connection_tuple[0] == websocket:
                    connections.remove(connection_tuple)
                    break

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, game_id: int):
        if game_id in self.active_connections:
            for websocket, player_name in self.active_connections[game_id]:
                print(f"Sending to {player_name}: {message}")  # Debugging line
                await websocket.send_text(message)
    
    def get_player_name(self, websocket: WebSocket) -> str:
        for connections in self.active_connections.values():
            for ws, player_name in connections:
                if ws == websocket:
                    return player_name
        return "Unknown Player"
    
    def get_players_in_game(self, game_id: int) -> List[str]:
        if game_id in self.active_connections:
            return [player_name for _, player_name in self.active_connections[game_id]]
        return []
