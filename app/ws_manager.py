from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(room, set()).add(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast(self, room: str, message: str):
        if room not in self.active_connections:
            return
        dead = []
        for ws in list(self.active_connections[room]):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(room, d)
