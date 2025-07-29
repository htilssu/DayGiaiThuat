import asyncio
from json import dump
from typing import Any, Coroutine

from app.core.agents.exercise_agent import ExerciseDetail as ExerciseSchema
from app.core.agents.exercise_agent import (
    GenerateExerciseQuestionAgent,
    get_exercise_agent,
)
from app.database.database import get_async_db, get_db
from app.database.repository import Repository
from app.models import Exercise
from app.models.exercise_model import Exercise as ExerciseModel
from app.models.lesson_model import Lesson
from app.schemas.exercise_schema import (
    CodeSubmissionRequest,
    CodeSubmissionResponse,
    CreateExerciseSchema,
    ExerciseDetail,
    TestCaseResult,
)
from app.schemas.lesson_schema import LessonBase
from app.services.topic_service import TopicService, get_topic_service
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload


async def run_code_in_docker(
    code: str, language: str, input_data: str, expected_output: str
) -> tuple[str, bool, str | None]:
    """
    Placeholder for running code in Docker for the given language and input.
    Returns (actual_output, passed, error)
    """
    # TODO: Implement Docker-based code execution for each language
    # For now, just echo input as output and always pass
    await asyncio.sleep(0.1)
    return input_data, input_data.strip() == expected_output.strip(), None


class ExerciseService:
    """
    Service xử lý các thao tác liên quan đến bài tập

    Attributes:
        exercise_agent (GenerateExerciseQuestionAgent): Agent tạo bài tập
        topic_service (TopicService): Service xử lý chủ đề
        repository (Repository): Repository xử lý dữ liệu bài tập
    """

    def __init__(
        self,
        exercise_agent: GenerateExerciseQuestionAgent,
        topic_service: TopicService,
        session: AsyncSession,
    ):
        self.exercise_agent = exercise_agent
        self.db = session
        self.topic_service = topic_service

    async def get_exercise(self, exercise_id: int) -> type[Exercise]:
        """
        Lấy thông tin bài tập theo ID

        Args:
            exercise_id (int): ID của bài tập

        Returns:
            ExerciseModel: Thông tin bài tập
        """
        exercise = await self.db.get(ExerciseModel, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy bài tập với ID {exercise_id}",
            )
        return exercise

    async def create_exercise(
        self, create_data: CreateExerciseSchema
    ) -> ExerciseSchema:
        """
        Tạo bài tập mới sử dụng AI agent

        Args:
            create_data (ExerciseDetail): Dữ liệu để tạo bài tập
            db (AsyncSession, optional): Phiên làm việc với database

        Returns:
            ExerciseSchema: Thông tin bài tập đã được tạo
        """
        # Lấy thông tin chủ đề
        topic = await self.topic_service.get_topic_by_id(create_data.topic_id)
        lesson = await self.db.execute(
            select(Lesson)
            .where(Lesson.id == create_data.lesson_id)
            .options(selectinload(Lesson.sections))
        )
        lesson = lesson.scalar_one_or_none()

        class SectionA(BaseModel):
            content: str
            answer: str | None = None
            explanation: str | None = None

        class LessonA(BaseModel):
            name: str | None = None
            description: str | None = None
            sections: list[SectionA]

        lesson_schema = LessonA(
            name=lesson.title if lesson else None,
            description=lesson.description if lesson else None,
            sections=[
                SectionA(
                    content=section.content,
                    answer=section.answer,
                    explanation=section.explanation,
                )
                for section in lesson.sections
            ],
        )

        if not topic:
            raise ValueError(f"Không tìm thấy chủ đề với ID {create_data.topic_id}")

        # Gọi agent để tạo bài tập và lưu vào database
        exercise_detail = await self.exercise_agent.act(
            session_id=create_data.session_id,
            topic=topic.name,
            difficulty=create_data.difficulty,
            lesson=lesson_schema.model_dump() if lesson else None,
        )

        exercise_model = ExerciseModel.exercise_from_schema(exercise_detail)

        self.db.add(exercise_model)
        await self.db.commit()

        return exercise_detail

    async def evaluate_submission(
        self, exercise_id: int, submission: CodeSubmissionRequest
    ) -> CodeSubmissionResponse:
        """
        Chấm code của học sinh với các test case của bài tập.
        """
        exercise = await self.get_exercise(exercise_id)
        if not exercise:
            raise ValueError(f"Không tìm thấy bài tập với ID {exercise_id}")

        # Assume exercise has a .case attribute with test cases (list of TestCase)
        test_cases = getattr(exercise, "case", None)
        if not test_cases:
            raise ValueError("Bài tập không có test case để kiểm tra")

        results = []
        all_passed = True
        for test_case in test_cases:
            input_data = getattr(test_case, "input_data", None) or getattr(
                test_case, "input", None
            )
            expected_output = getattr(test_case, "output_data", None) or getattr(
                test_case, "output", None
            )
            actual_output, passed, error = await run_code_in_docker(
                submission.code, submission.language, input_data, expected_output
            )
            results.append(
                TestCaseResult(
                    input=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    passed=passed,
                    error=error,
                )
            )
            if not passed:
                all_passed = False
        return CodeSubmissionResponse(results=results, all_passed=all_passed)


def get_exercise_service(
    db: AsyncSession = Depends(get_async_db),
    topic_service: TopicService = Depends(get_topic_service),
    exercise_agent: GenerateExerciseQuestionAgent = Depends(get_exercise_agent),
):
    return ExerciseService(exercise_agent, topic_service, db)
