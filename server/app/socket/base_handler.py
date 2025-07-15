from typing import Any
from fastapi import WebSocket


class BaseWebSocketHandler:
    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

    async def handle(self, websocket: WebSocket, message: Any, next: Any):
        raise NotImplementedError("handle() must be implemented by subclasses")
