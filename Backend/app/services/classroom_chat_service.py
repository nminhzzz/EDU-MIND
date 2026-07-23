import asyncio
from typing import Dict, List
from fastapi import WebSocket


class ClassroomChatManager:
    def __init__(self):
        # Maps classroom_id -> list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Async lock for thread-safe mutations
        self.lock = asyncio.Lock()

    async def connect(self, classroom_id: int, websocket: WebSocket):
        async with self.lock:
            if classroom_id not in self.active_connections:
                self.active_connections[classroom_id] = []
            self.active_connections[classroom_id].append(websocket)

    async def disconnect(self, classroom_id: int, websocket: WebSocket):
        async with self.lock:
            if classroom_id in self.active_connections:
                if websocket in self.active_connections[classroom_id]:
                    self.active_connections[classroom_id].remove(websocket)
                if not self.active_connections[classroom_id]:
                    del self.active_connections[classroom_id]

    async def broadcast(self, classroom_id: int, message: dict):
        async with self.lock:
            # We copy the list to avoid mutating during iteration
            connections = list(self.active_connections.get(classroom_id, []))
        if not connections:
            return

        # Broadcast concurrently, handle disconnections/errors gracefully
        async def safe_send(websocket: WebSocket):
            try:
                await websocket.send_json(message)
            except Exception:
                pass

        await asyncio.gather(*(safe_send(ws) for ws in connections), return_exceptions=True)


classroom_chat_manager = ClassroomChatManager()
