from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.schemas.exercise import CreateExerciseSchema
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("")
async def get_exercise(
        data: CreateExerciseSchema = None,
        exercise_service: ExerciseService = Depends(ExerciseService),
):
    if data is None:
        return JSONResponse("Invalid request data", status_code=400)
    exercise = await exercise_service.create_exercise(data)

    return exercise
