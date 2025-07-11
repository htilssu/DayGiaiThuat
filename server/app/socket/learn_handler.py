from app.socket.base_handler import BaseWebSocketHandler
from app.services.lesson_service import get_lesson_service
from app.database.database import get_independent_db_session
from app.routers.websocket_router import active_connections
from app.models.lesson_model import Lesson
from fastapi import WebSocket, HTTPException
from typing import Any, Callable
from sqlalchemy import select
from app.models.user_topic_model import UserTopic


class LearnConnectionHandler(BaseWebSocketHandler):
    async def handle(self, websocket: WebSocket, message: Any, next: Callable):
        message_type = message.get("type", "")
        if message_type == "learn.complete_lesson":
            lesson_id = message.get("lesson_id")
            user_id = active_connections.inverse[websocket]
            async with get_independent_db_session() as db_session:
                lesson = (
                    await db_session.execute(
                        select(Lesson).where(
                            Lesson.id == lesson_id,
                        )
                    )
                ).scalar_one_or_none()
                if lesson is None:
                    raise HTTPException(status_code=404, detail="Lesson not found")

                lesson.user_lessons
                topic_id = lesson.topic_id
                user_topic = (
                    await db_session.execute(
                        select(UserTopic).where(
                            UserTopic.user_id == user_id, UserTopic.topic_id == topic_id
                        )
                    )
                ).scalar_one_or_none()
                if user_topic is None:
                    raise HTTPException(status_code=404, detail="User topic not found")

                user_topic.completed_lessons += 1
                user_topic.progress = int(
                    user_topic.completed_lessons / len(lesson.topic.lessons) * 100
                )
                await db_session.commit()

        if message_type == "learn.start_lesson":
            await self.send_json(websocket, {"type": "learn.start_lesson.ack"})
            async with get_independent_db_session() as db_session:
                get_lesson_service(db_session).start_lesson(
                    lesson_id=message.get("lesson_id"),
                    user_id=self.user.id,
                )
        await next()
