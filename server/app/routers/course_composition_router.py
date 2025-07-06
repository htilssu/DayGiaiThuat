from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.schemas.course_schema import CourseCompositionRequestSchema, CourseCompositionResponseSchema

router = APIRouter()

@router.post("/compose-course", response_model=CourseCompositionResponseSchema)
async def compose_course(
    request: CourseCompositionRequestSchema,
    db: Session = Depends(get_db)
):
    """
    Generates a course composition, including topics and lessons.
    """
    try:
        agent = CourseCompositionAgent()
        result = await agent.act(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
