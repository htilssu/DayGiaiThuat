from typing import Dict, Any
import asyncio
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.database.database import get_db
from app.core.agents.course_composition_agent import (
    CourseCompositionAgent,
    CourseCompositionRequestSchema,
)
from app.services.topic_service import TopicService, get_topic_service
from app.services.lesson_service import LessonService, get_lesson_service
from app.schemas.topic_schema import CreateTopicSchema
from app.models.course_model import Course


class CourseCompositionService:
    """Service để tự động soạn bài giảng cho khóa học"""

    def __init__(
        self, db: Session, topic_service: TopicService, lesson_service: LessonService
    ):
        self.db = db
        self.topic_service = topic_service
        self.lesson_service = lesson_service
        self.composition_agent = CourseCompositionAgent(db)

    async def generate_course_content(self, course_id: str) -> Dict[str, Any]:
        """Tự động tạo nội dung cho khóa học sau khi upload document"""
        return await self.compose_course_content(int(course_id))

    async def compose_course_content(self, course_id: int) -> Dict[str, Any]:
        """Tự động soạn nội dung cho khóa học"""
        try:
            # Lấy thông tin khóa học
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            print(f"🎯 Bắt đầu soạn nội dung cho khóa học: {course.title}")

            # Tạo request cho agent
            composition_request = CourseCompositionRequestSchema(
                course_id=course_id,
                course_title=course.title,
                course_description=course.description or "",
                course_level=course.level,
                max_topics=8,
                lessons_per_topic=4,
            )

            # Sử dụng agent để tạo topics
            print("🔄 Đang phân tích nội dung và tạo topics...")
            agent_result = await asyncio.to_thread(
                self.composition_agent.act, composition_request
            )

            if agent_result["status"] != "success":
                return {
                    "success": False,
                    "course_id": course_id,
                    "message": "Không thể tạo topics từ agent",
                    "errors": agent_result.get("errors", []),
                }

            # Lưu topics vào database
            created_topics = []
            for topic_info in agent_result["topics"]:
                try:
                    topic_data = CreateTopicSchema(
                        name=topic_info["topic_info"]["name"],
                        description=topic_info["topic_info"]["description"],
                        prerequisites=topic_info["topic_info"].get("prerequisites"),
                        course_id=course_id,
                        external_id=f"topic_{len(created_topics) + 1}",
                    )

                    topic = await self.topic_service.create_topic(topic_data)
                    created_topics.append(topic)
                    print(f"✅ Đã tạo topic: {topic.name}")

                except Exception as e:
                    print(f"❌ Lỗi khi tạo topic: {str(e)}")
                    continue

            return {
                "success": True,
                "course_id": course_id,
                "message": f"Đã hoàn thành soạn nội dung cho khóa học '{course.title}'",
                "statistics": {
                    "total_topics": len(created_topics),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "course_id": course_id,
                "message": "Lỗi hệ thống",
                "errors": [str(e)],
            }


def get_course_composition_service(
    db: Session = Depends(get_db),
    topic_service: TopicService = Depends(get_topic_service),
    lesson_service: LessonService = Depends(get_lesson_service),
) -> CourseCompositionService:
    return CourseCompositionService(db, topic_service, lesson_service)
