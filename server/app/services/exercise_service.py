from fastapi import Depends

from app.schemas.exercise_schema import (
    CreateExerciseSchema,
    CodeSubmissionRequest,
    CodeSubmissionResponse,
    TestCaseResult,
)
from app.core.agents.exercise_agent import ExerciseDetail as ExerciseSchema
from app.models.exercise_model import Exercise as ExerciseModel
from app.core.agents.exercise_agent import (
    GenerateExerciseQuestionAgent,
    get_exercise_agent,
)
from app.services.topic_service import TopicService, get_topic_service
from app.database.repository import Repository
from app.database.database import get_db
from sqlalchemy.orm import Session

import asyncio
import os
import requests

JUDGE0_API_URL = os.getenv("JUDGE0_API_URL")


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


async def run_code_in_docker(code: str, language: str, input_data: str, expected_output: str) -> tuple[str, bool, str | None]:
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
        repository: Repository[ExerciseModel],
    ):
        self.exercise_agent = exercise_agent
        self.topic_service = topic_service
        self.repository = repository

    async def get_exercise(self, exercise_id: int) -> ExerciseModel:
        """
        Lấy thông tin bài tập theo ID

        Args:
            exercise_id (int): ID của bài tập

        Returns:
            ExerciseModel: Thông tin bài tập
        """
        exercise = self.repository.get(exercise_id)
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

        if not topic:
            raise ValueError(f"Không tìm thấy chủ đề với ID {create_data.topic_id}")

        # Gọi agent để tạo bài tập và lưu vào database
        exercise_detail = await self.exercise_agent.act(
            session_id=create_data.session_id,
            topic=topic.name,
            difficulty=create_data.difficulty,
        )

        exercise_model = ExerciseModel.exercise_from_schema(exercise_detail)
        exercise_model.topic_id = topic.id

        await self.repository.create_async(exercise_model)

        return exercise_model

    async def evaluate_submission(self, exercise_id: int, submission: CodeSubmissionRequest) -> CodeSubmissionResponse:
        """
        Chấm code của học sinh với các test case của bài tập.
        """
        exercise = await self.get_exercise(exercise_id)
        if not exercise:
            raise ValueError(f"Không tìm thấy bài tập với ID {exercise_id}")

        # Assume exercise has a .case attribute with test cases (list of TestCase)
        test_cases = getattr(exercise, 'case', None)
        if not test_cases:
            raise ValueError("Bài tập không có test case để kiểm tra")

        results = []
        all_passed = True
        for test_case in test_cases:
            input_data = getattr(test_case, 'input_data', None) or getattr(test_case, 'input', None)
            expected_output = getattr(test_case, 'output_data', None) or getattr(test_case, 'output', None)
            actual_output, passed, error = await run_code_in_docker(
                submission.code, submission.language, input_data, expected_output
            )
            results.append(TestCaseResult(
                input=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                passed=passed,
                error=error,
            ))
            if not passed:
                all_passed = False
        return CodeSubmissionResponse(results=results, all_passed=all_passed)

    async def evaluate_submission_with_judge0(self, exercise_id: int, submission: CodeSubmissionRequest) -> CodeSubmissionResponse:
        """
        Chấm code của học sinh với các test case của bài tập sử dụng Judge0.
        """
        exercise = await self.get_exercise(exercise_id)
        if not exercise:
            raise ValueError(f"Không tìm thấy bài tập với ID {exercise_id}")

        test_cases = getattr(exercise, 'case', None)
        if not test_cases:
            raise ValueError("Bài tập không có test case để kiểm tra")

        results = []
        all_passed = True

        for test_case in test_cases:
            input_data = getattr(test_case, 'input_data', None) or getattr(test_case, 'input', None)
            expected_output = getattr(test_case, 'output_data', None) or getattr(test_case, 'output', None)

            # Submit to Judge0
            response = requests.post(
                f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true",
                headers={"Content-Type": "application/json"},
                json={
                    "source_code": submission.code,
                    "language_id": get_language_id(submission.language),
                    "stdin": input_data
                }
            )

            if not response.ok:
                results.append(TestCaseResult(
                    input=input_data,
                    expected_output=expected_output,
                    actual_output="",
                    passed=False,
                    error=f"Judge0 error: {response.text}"
                ))
                all_passed = False
                continue

            result_data = response.json()
            actual_output = (result_data.get("stdout") or "").strip()
            error = (result_data.get("stderr") or result_data.get("compile_output") or "")
            passed = actual_output == (expected_output or "").strip() and not error

            results.append(TestCaseResult(
                input=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                passed=passed,
                error=error
            ))

            if not passed:
                all_passed = False

        return CodeSubmissionResponse(results=results, all_passed=all_passed)


def get_exercise_service(
    db: Session = Depends(get_db),
    topic_service: TopicService = Depends(get_topic_service),
    exercise_agent: GenerateExerciseQuestionAgent = Depends(get_exercise_agent),
):
    repository = Repository(ExerciseModel, db)
    return ExerciseService(exercise_agent, topic_service, repository)
