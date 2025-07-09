from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.orm import selectinload
import uuid
from fastapi import HTTPException, status

from app.database.database import get_async_db
from app.models.lesson_model import Lesson, LessonSection
from app.models.lesson_generation_state_model import LessonGenerationState
from app.schemas.lesson_schema import (
    CreateLessonSchema,
    UpdateLessonSchema,
    LessonResponseSchema,
    GenerateLessonRequestSchema,
    LessonSectionSchema,
    Options,
    ExerciseResponse,
)
from app.core.agents.lesson_generating_agent import get_lesson_generating_agent


from app.services.topic_service import get_topic_service, TopicService


class LessonService:
    def __init__(self, db: AsyncSession, topic_service: TopicService):
        self.db = db
        self.agent = get_lesson_generating_agent()
        self.topic_service = topic_service

    async def generate_lesson(
        self, request: GenerateLessonRequestSchema, topic_id: int, order: int
    ) -> LessonResponseSchema:
        """
        Generate a lesson using the RAG AI agent and log the state.
        """
        # Validate topic
        topic = await self.topic_service.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        if not request.session_id:
            request.session_id = str(uuid.uuid4())

        # Create initial state
        generation_state = LessonGenerationState(
            session_id=request.session_id,
            topic_id=topic_id,
            status="in_progress",
            request_data=request.model_dump_json(),
        )
        self.db.add(generation_state)
        await self.db.commit()
        await self.db.refresh(generation_state)

        try:
            # Generate lesson using the agent
            lesson_data = await self.agent.act(**request.model_dump())

            # Update the generated lesson with proper topic_id and order
            lesson_data.topic_id = topic_id
            lesson_data.order = order

            # Create the lesson in database
            lesson = await self.create_lesson(lesson_data)

            # Update state to completed
            generation_state.status = "completed"
            generation_state.lesson_id = lesson.id
            await self.db.commit()

            return lesson

        except Exception as e:
            # Update state to failed
            generation_state.status = "failed"
            await self.db.commit()
            # Re-raise the exception
            raise e

    async def create_lesson(
        self, lesson_data: CreateLessonSchema
    ) -> LessonResponseSchema:
        """
        Create a new lesson with sections.
        """
        # Create lesson
        lesson = Lesson(
            external_id=lesson_data.external_id,
            title=lesson_data.title,
            description=lesson_data.description,
            topic_id=lesson_data.topic_id,
            order=lesson_data.order,
            next_lesson_id=lesson_data.next_lesson_id,
            prev_lesson_id=lesson_data.prev_lesson_id,
        )

        self.db.add(lesson)
        await self.db.flush()  # Get the lesson ID

        # Create lesson sections
        for section_data in lesson_data.sections:
            # Chuyển đổi options từ Pydantic model sang dict nếu tồn tại
            options_dict = None
            if section_data.options:
                options_dict = section_data.options.model_dump()

            section = LessonSection(
                lesson_id=lesson.id,
                type=section_data.type,
                content=section_data.content,
                order=section_data.order,
                options=options_dict,
                answer=section_data.answer,
                explanation=section_data.explanation,
            )
            self.db.add(section)

        await self.db.commit()
        await self.db.refresh(lesson)

        # Tải rõ ràng các mối quan hệ trước khi chuyển đổi
        sections = await self.db.execute(
            select(LessonSection).where(LessonSection.lesson_id == lesson.id)
        )
        sections_list = sections.scalars().all()

        # Tạo sections data
        sections_data = []
        for section in sections_list:
            section_data = {
                "type": section.type,
                "content": section.content,
                "order": section.order,
                "options": None,
                "answer": section.answer,
                "explanation": section.explanation,
            }

            # Xử lý options nếu có
            if section.options and isinstance(section.options, dict):
                if all(key in section.options for key in ["A", "B", "C", "D"]):
                    section_data["options"] = Options(
                        A=section.options["A"],
                        B=section.options["B"],
                        C=section.options["C"],
                        D=section.options["D"],
                    )

            sections_data.append(LessonSectionSchema(**section_data))

        # Tạo một đối tượng response thủ công thay vì dùng model_validate trực tiếp
        response = LessonResponseSchema(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            topic_id=lesson.topic_id,
            order=lesson.order,
            next_lesson_id=lesson.next_lesson_id,
            prev_lesson_id=lesson.prev_lesson_id,
            sections=sections_data,
            exercises=[],  # Ban đầu không có exercises
        )

        return response

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[LessonResponseSchema]:
        """
        Get a lesson by ID.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Tạo đối tượng response thủ công thay vì dùng model_validate
        sections_data = []
        for section in lesson.sections:
            section_data = {
                "type": section.type,
                "content": section.content,
                "order": section.order,
                "options": None,
                "answer": section.answer,
                "explanation": section.explanation,
            }

            # Xử lý options nếu có
            if section.options and isinstance(section.options, dict):
                if all(key in section.options for key in ["A", "B", "C", "D"]):
                    section_data["options"] = Options(
                        A=section.options["A"],
                        B=section.options["B"],
                        C=section.options["C"],
                        D=section.options["D"],
                    )

            sections_data.append(LessonSectionSchema(**section_data))

        response = LessonResponseSchema(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            topic_id=lesson.topic_id,
            order=lesson.order,
            next_lesson_id=lesson.next_lesson_id,
            prev_lesson_id=lesson.prev_lesson_id,
            sections=sections_data,
            exercises=[
                ExerciseResponse(
                    id=exercise.id,
                    name=exercise.name,
                    description=exercise.description,
                    difficulty=exercise.difficulty,
                    constraint=exercise.constraint,
                    suggest=exercise.suggest,
                    lesson_id=exercise.lesson_id,
                )
                for exercise in lesson.exercises
            ],
        )

        return response

    async def get_lesson_by_external_id(
        self, external_id: str
    ) -> Optional[LessonResponseSchema]:
        """
        Get a lesson by external ID.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.external_id == external_id)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Tạo đối tượng response thủ công thay vì dùng model_validate
        sections_data = []
        for section in lesson.sections:
            section_data = {
                "type": section.type,
                "content": section.content,
                "order": section.order,
                "options": None,
                "answer": section.answer,
                "explanation": section.explanation,
            }

            # Xử lý options nếu có
            if section.options and isinstance(section.options, dict):
                if all(key in section.options for key in ["A", "B", "C", "D"]):
                    section_data["options"] = Options(
                        A=section.options["A"],
                        B=section.options["B"],
                        C=section.options["C"],
                        D=section.options["D"],
                    )

            sections_data.append(LessonSectionSchema(**section_data))

        response = LessonResponseSchema(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            topic_id=lesson.topic_id,
            order=lesson.order,
            next_lesson_id=lesson.next_lesson_id,
            prev_lesson_id=lesson.prev_lesson_id,
            sections=sections_data,
            exercises=[
                ExerciseResponse(
                    id=exercise.id,
                    name=exercise.name,
                    description=exercise.description,
                    difficulty=exercise.difficulty,
                    constraint=exercise.constraint,
                    suggest=exercise.suggest,
                    lesson_id=exercise.lesson_id,
                )
                for exercise in lesson.exercises
            ],
        )

        return response

    async def get_lessons_by_topic(self, topic_id: int) -> List[LessonResponseSchema]:
        """
        Get all lessons for a topic.
        """
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
            .options(selectinload(Lesson.sections), selectinload(Lesson.exercises))
        )
        result = await self.db.execute(stmt)
        lessons = result.scalars().all()

        lesson_responses = []

        for lesson in lessons:
            # Tạo đối tượng response thủ công thay vì dùng model_validate
            sections_data = []
            for section in lesson.sections:
                section_data = {
                    "type": section.type,
                    "content": section.content,
                    "order": section.order,
                    "options": None,
                    "answer": section.answer,
                    "explanation": section.explanation,
                }

                # Xử lý options nếu có
                if section.options and isinstance(section.options, dict):
                    if all(key in section.options for key in ["A", "B", "C", "D"]):
                        section_data["options"] = Options(
                            A=section.options["A"],
                            B=section.options["B"],
                            C=section.options["C"],
                            D=section.options["D"],
                        )

                sections_data.append(LessonSectionSchema(**section_data))

            response = LessonResponseSchema(
                id=lesson.id,
                external_id=lesson.external_id,
                title=lesson.title,
                description=lesson.description,
                topic_id=lesson.topic_id,
                order=lesson.order,
                next_lesson_id=lesson.next_lesson_id,
                prev_lesson_id=lesson.prev_lesson_id,
                sections=sections_data,
                exercises=[
                    ExerciseResponse(
                        id=exercise.id,
                        name=exercise.name,
                        description=exercise.description,
                        difficulty=exercise.difficulty,
                        constraint=exercise.constraint,
                        suggest=exercise.suggest,
                        lesson_id=exercise.lesson_id,
                    )
                    for exercise in lesson.exercises
                ],
            )
            lesson_responses.append(response)

        return lesson_responses

    async def update_lesson(
        self, lesson_id: int, lesson_data: UpdateLessonSchema
    ) -> Optional[LessonResponseSchema]:
        """
        Update a lesson.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return None

        # Update fields
        for field, value in lesson_data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)

        await self.db.commit()
        await self.db.refresh(lesson)

        # Tải rõ ràng các mối quan hệ
        await self.db.refresh(lesson, ["sections", "exercises"])

        # Tạo đối tượng response thủ công thay vì dùng model_validate
        sections_data = []
        for section in lesson.sections:
            section_data = {
                "type": section.type,
                "content": section.content,
                "order": section.order,
                "options": None,
                "answer": section.answer,
                "explanation": section.explanation,
            }

            # Xử lý options nếu có
            if section.options and isinstance(section.options, dict):
                if all(key in section.options for key in ["A", "B", "C", "D"]):
                    section_data["options"] = Options(
                        A=section.options["A"],
                        B=section.options["B"],
                        C=section.options["C"],
                        D=section.options["D"],
                    )

            sections_data.append(LessonSectionSchema(**section_data))

        response = LessonResponseSchema(
            id=lesson.id,
            external_id=lesson.external_id,
            title=lesson.title,
            description=lesson.description,
            topic_id=lesson.topic_id,
            order=lesson.order,
            next_lesson_id=lesson.next_lesson_id,
            prev_lesson_id=lesson.prev_lesson_id,
            sections=sections_data,
            exercises=[
                ExerciseResponse(
                    id=exercise.id,
                    name=exercise.name,
                    description=exercise.description,
                    difficulty=exercise.difficulty,
                    constraint=exercise.constraint,
                    suggest=exercise.suggest,
                    lesson_id=exercise.lesson_id,
                )
                for exercise in lesson.exercises
            ],
        )

        return response

    async def delete_lesson(self, lesson_id: int) -> bool:
        """
        Delete a lesson.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if not lesson:
            return False

        await self.db.delete(lesson)
        await self.db.commit()

        return True


def get_lesson_service(
    db: AsyncSession = Depends(get_async_db),
    topic_service: TopicService = Depends(get_topic_service),
) -> LessonService:
    """
    Dependency injection for LessonService

    Args:
        db: Async database session
        topic_service: Topic service instance

    Returns:
        LessonService: Service instance
    """
    return LessonService(db=db, topic_service=topic_service)
