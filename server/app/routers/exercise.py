from fastapi import APIRouter, Depends

from app.core.agents.exercise_generator import GenerateExerciseQuestionAgent, get_exercise_agent
from app.schemas.exercise import GetExerciseSchema

router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("")
async def get_exercise(data: GetExerciseSchema = None,
                       exercise_agent: GenerateExerciseQuestionAgent = Depends(get_exercise_agent)):
    da = await exercise_agent.act(session_id=data.session_id, topic=data.topic, difficulty=data.difficulty)

    return da
