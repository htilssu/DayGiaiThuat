from fastapi import Depends

from app.schemas.exercise_schema import CreateExerciseSchema
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
        exercise = await self.repository.get(exercise_id)
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


def get_exercise_service(
    db: Session = Depends(get_db),
    topic_service: TopicService = Depends(get_topic_service),
    exercise_agent: GenerateExerciseQuestionAgent = Depends(get_exercise_agent),
):
    repository = Repository(ExerciseModel, db)
    return ExerciseService(exercise_agent, topic_service, repository)
