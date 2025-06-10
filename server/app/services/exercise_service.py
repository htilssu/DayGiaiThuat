from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.exercise import CreateExerciseSchema, Exercise as ExerciseSchema
from app.models.exercise import Exercise as ExerciseModel
from app.core.agents.exercise_generator import (
    GenerateExerciseQuestionAgent,
    get_exercise_agent,
)


class ExerciseService:
    def __init__(
        self,
        db: Session = Depends(get_db),
        exercise_agent: GenerateExerciseQuestionAgent = Depends(get_exercise_agent),
    ):
        self.db = db
        self.exercise_agent = exercise_agent

    def get_exercise(self, exercise_id: str) -> ExerciseModel:
        exercise = (
            self.db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id).first()
        )
        return exercise

    async def create_exercise(
        self, create_data: CreateExerciseSchema
    ) -> ExerciseSchema:
        exercise = await self.exercise_agent.act(
            session_id=create_data.session_id,
            topic=create_data.topic,
            difficulty=create_data.difficulty,
        )

        # exercise_model = Exercise(**exercise.model_dump())

        # self.db.add(exercise_model)
        # self.db.commit()
        # self.db.refresh(exercise_model)
        return exercise
