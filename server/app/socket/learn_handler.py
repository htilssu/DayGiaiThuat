from app.socket.base_handler import BaseWebSocketHandler
from app.services.lesson_service import get_lesson_service
from app.database.database import get_independent_db_session

from fastapi import WebSocket
from typing import Any, Callable


class LearnConnectionHandler(BaseWebSocketHandler):
    async def handle(self, websocket: WebSocket, message: Any, next: Callable):
        message_type = message.get("type", "")
        if message_type == "learn.complete_lesson":
            lesson_id = message.get("lesson_id")
            async with get_independent_db_session() as db_session:
                get_lesson_service(db_session).complete_lesson(

        if message_type == "learn.start_lesson":
            await self.send_json(websocket, {"type": "learn.start_lesson.ack"})
            async with get_independent_db_session() as db_session:
                get_lesson_service(db_session).start_lesson(
                    lesson_id=message.get("lesson_id"),
                    user_id=self.user.id,
                )
        await next()
