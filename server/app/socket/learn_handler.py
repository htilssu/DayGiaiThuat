from app.socket.base_handler import BaseWebSocketHandler
from app.services.lesson_service import get_lesson_service
from app.database.database import get_independent_db_session
from fastapi import WebSocket
from typing import Any, Callable


class LearnConnectionHandler(BaseWebSocketHandler):
    async def handle(self, websocket: WebSocket, message: Any, next: Callable):
        from app.routers.websocket_router import active_connections

        message_type = message.get("type", "")
        user_id_str = active_connections.inverse.get(websocket)
        if not user_id_str:
            # Handle case where user is not found
            await self.send_json(
                websocket, {"type": "error", "message": "User not authenticated"}
            )
            return
        user_id = int(user_id_str)

        if message_type == "learn.complete_lesson":
            lesson_id = message.get("lesson_id")
            if not lesson_id:
                await self.send_json(
                    websocket, {"type": "error", "message": "Lesson ID is missing"}
                )
                return

            async with get_independent_db_session() as db_session:
                lesson_service = get_lesson_service(db_session)
                result = await lesson_service.complete_lesson(
                    lesson_id=lesson_id, user_id=user_id
                )
                if result is not None:
                    await self.send_json(websocket, result)

        elif message_type == "learn.start_lesson":
            lesson_id = message.get("lesson_id")
            if not lesson_id:
                await self.send_json(
                    websocket, {"type": "error", "message": "Lesson ID is missing"}
                )
                return

            async with get_independent_db_session() as db_session:
                lesson_service = get_lesson_service(db_session)
                await lesson_service.start_lesson(lesson_id=lesson_id, user_id=user_id)
            await self.send_json(websocket, {"type": "learn.start_lesson.ack"})

        await next()
