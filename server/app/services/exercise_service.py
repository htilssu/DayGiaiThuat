import asyncio

import requests
from app.core.agents.exercise_agent import ExerciseDetail as ExerciseSchema
from app.core.agents.exercise_agent import (
    GenerateExerciseQuestionAgent,
    get_exercise_agent,
)
from app.database.database import get_async_db, get_independent_db_session
from app.core.config import settings
from app.models import Exercise, ExerciseTestCase
from app.models.exercise_model import Exercise as ExerciseModel
from app.models.lesson_model import Lesson
from app.models.exercise_test_case_model import ExerciseTestCase
from app.schemas.exercise_schema import (
    CodeSubmissionRequest,
    CodeSubmissionResponse,
    CreateExerciseSchema,
    TestCaseResult,
)
from app.schemas.exercise_schema import ExerciseUpdate
from app.services.topic_service import TopicService, get_topic_service
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

JUDGE0_API_URL = (settings.JUDGE0_API_URL or "").rstrip("/")


def get_language_id(language: str) -> int:
    # Map your language strings to Judge0 language IDs
    language_map = {
        "python": 71,
        "javascript": 63,
        "c": 50,
        "cpp": 54,
        "java": 62,
        # Add more mappings as needed
    }
    return language_map.get(language.lower(), 71)


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

    async def get_exercise(self, exercise_id: int) -> Exercise:
        """
        Lấy thông tin bài tập theo ID

        Args:
            exercise_id (int): ID của bài tập

        Returns:
            ExerciseModel: Thông tin bài tập
        """
        exercise = await self.db.execute(
            select(ExerciseModel)
            .where(ExerciseModel.id == exercise_id)
            .options(selectinload(ExerciseModel.test_cases))
        )
        exercise = exercise.scalars().first()
        if not exercise:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy bài tập với ID {exercise_id}",
            )
        return exercise

    async def list_exercises(
        self, page: int = 1, limit: int = 12
    ) -> list[ExerciseModel]:
        offset = max(0, (page - 1) * limit)
        result = await self.db.execute(
            select(ExerciseModel)
            .order_by(ExerciseModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_exercise(
        self, exercise_id: int, data: ExerciseUpdate
    ) -> ExerciseModel:
        exercise = await self.db.get(ExerciseModel, exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(exercise, field):
                setattr(exercise, field, value)

        await self.db.commit()
        await self.db.refresh(exercise)
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

        lesson_schema = None
        if lesson:
            lesson_schema = LessonA(
                name=lesson.title,
                description=lesson.description,
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
            lesson=lesson_schema.model_dump() if lesson_schema else None,
        )

        exercise_model = ExerciseModel.exercise_from_schema(exercise_detail)
        exercise_model.test_cases = [
            ExerciseTestCase(**testc) for testc in exercise_detail.case
        ]
        self.db.add(exercise_model)
        await self.db.commit()
        await self.db.refresh(exercise_model)

        # Persist generated test cases (if provided by agent)
        try:
            cases = getattr(exercise_detail, "case", None) or []
            if isinstance(cases, list) and exercise_model.id:
                for tc in cases:
                    input_data = getattr(tc, "input", None) or getattr(
                        tc, "input_data", None
                    )
                    output_data = (
                        getattr(tc, "expected_output", None)
                        or getattr(tc, "output_data", None)
                        or getattr(tc, "output", None)
                    )
                    explain = getattr(tc, "explain", None)
                    if input_data is None or output_data is None:
                        continue
                    self.db.add(
                        ExerciseTestCase(
                            exercise_id=exercise_model.id,
                            input_data=str(input_data),
                            output_data=str(output_data),
                            explain=explain,
                        )
                    )
                await self.db.commit()
        except Exception:
            # Don't block exercise creation if test case persistence fails
            await self.db.rollback()

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

        # Ưu tiên dùng test cases quan hệ nếu có; fallback sang JSON `case`
        test_cases = getattr(exercise, "test_cases", None) or getattr(
            exercise, "case", None
        )
        if not test_cases:
            raise ValueError("Bài tập không có test case để kiểm tra")

        results = []
        all_passed = True
        for test_case in test_cases:
            input_data = (
                getattr(test_case, "input_data", None)
                or getattr(test_case, "input", None)
                or (test_case.get("input") if isinstance(test_case, dict) else None)
            )
            expected_output = (
                getattr(test_case, "output_data", None)
                or getattr(test_case, "output", None)
                or (test_case.get("output") if isinstance(test_case, dict) else None)
            )
            if input_data is None or expected_output is None:
                # Bỏ qua test case không hợp lệ
                continue
            actual_output, passed, error = await run_code_in_docker(
                submission.code,
                submission.language,
                str(input_data),
                str(expected_output),
            )
            results.append(
                TestCaseResult(
                    input=str(input_data),
                    expected_output=str(expected_output),
                    actual_output=str(actual_output),
                    passed=passed,
                    error=error,
                )
            )
            if not passed:
                all_passed = False
        return CodeSubmissionResponse(results=results, all_passed=all_passed)


async def evaluate_submission_with_judge0(
    exercise_id: int, submission: CodeSubmissionRequest
) -> CodeSubmissionResponse:
    """
    Chấm code của học sinh với các test case của bài tập sử dụng Judge0.
    """
    async with get_independent_db_session() as db:
        exercise = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
        exercise = exercise.scalar_one_or_none()
    if not exercise:
        raise ValueError(f"Không tìm thấy bài tập với ID {exercise_id}")

    test_cases = getattr(exercise, "test_cases", None) or getattr(
        exercise, "case", None
    )
    if not test_cases:
        raise ValueError("Bài tập không có test case để kiểm tra")

    results = []
    all_passed = True

    for test_case in test_cases:
        input_data = (
            getattr(test_case, "input_data", None)
            or getattr(test_case, "input", None)
            or (test_case.get("input") if isinstance(test_case, dict) else None)
        )
        expected_output = (
            getattr(test_case, "output_data", None)
            or getattr(test_case, "output", None)
            or (test_case.get("output") if isinstance(test_case, dict) else None)
        )

        # Submit to Judge0
        response = requests.post(
            f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true",
            headers={"Content-Type": "application/json"},
            json={
                "source_code": submission.code,
                "language_id": get_language_id(submission.language),
                "stdin": input_data,
            },
        )

        if not response.ok:
            results.append(
                TestCaseResult(
                    input=str(input_data) if input_data is not None else "",
                    expected_output=(
                        str(expected_output) if expected_output is not None else ""
                    ),
                    actual_output="",
                    passed=False,
                    error=f"Judge0 error: {response.text}",
                )
            )
            all_passed = False
            continue

        result_data = response.json()
        actual_output = (result_data.get("stdout") or "").strip()
        error = result_data.get("stderr") or result_data.get("compile_output") or ""
        passed = actual_output == (str(expected_output or "").strip()) and not error

        results.append(
            TestCaseResult(
                input=str(input_data) if input_data is not None else "",
                expected_output=(
                    str(expected_output) if expected_output is not None else ""
                ),
                actual_output=str(actual_output),
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
