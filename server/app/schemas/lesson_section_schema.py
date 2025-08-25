from typing import Optional, Dict

from pydantic import BaseModel


class Options(BaseModel):
    A: str
    B: str
    C: str
    D: str


class BaseLessonSection(BaseModel):
    lesson_id: int
    type: str
    content: str
    order: int
    options: Optional[Dict[str, str]] = None
    exercise_id: Optional[int] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class LessonSectionResponse(BaseLessonSection):
    id: int
