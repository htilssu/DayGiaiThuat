from app.socket.base_handler import BaseWebSocketHandler
from app.services.lesson_service import get_lesson_service
from app.database.database import get_async_db, get_independent_db_session

from fastapi import WebSocket
from typing import Any, Callable


class LearnConnectionHandler(BaseWebSocketHandler):
    async def handle(self, websocket: WebSocket, message: Any, next: Callable):
        message_type = message.get("type", "")
        if message_type == "lesson.complete":
            await self.send_json(websocket, {"type": "lesson.complete.ack"})
            async with get_independent_db_session() as db_session:
                get_lesson_service(db_session).mark_lesson_completed(
                    lesson_id=message.get("lesson_id"),
                    user_id=self.user.id,
                )
        await next()
