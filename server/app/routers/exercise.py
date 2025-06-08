from fastapi import APIRouter, Depends

from app.core.agents.exercise_generator import (
    GenerateExerciseQuestionAgent,
    get_exercise_agent,
)
from app.schemas.exercise import GetExerciseSchema
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("")
async def get_exercise(
    data: GetExerciseSchema = None,
    exercise_service: ExerciseService = Depends(ExerciseService),
):
    exercise = await exercise_service.create_exercise(data)

    return exercise
