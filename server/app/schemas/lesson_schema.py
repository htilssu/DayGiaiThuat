from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class LessonSectionSchema(BaseModel):
    type: str  # "text", "code", "image", "quiz"
    content: str
    order: int
    options: Optional[Dict[str, Any]] = None
    answer: Optional[int] = None
    explanation: Optional[str] = None


class CreateLessonSchema(BaseModel):
    external_id: str
    title: str
    description: str
    topic_id: int
    order: int
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None
    sections: List[LessonSectionSchema]


class UpdateLessonSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None


class LessonResponseSchema(BaseModel):
    id: int
    external_id: str
    title: str
    description: str
    topic_id: int
    order: int
    next_lesson_id: Optional[str] = None
    prev_lesson_id: Optional[str] = None
    sections: List[LessonSectionSchema]

    class Config:
        from_attributes = True


class GenerateLessonRequestSchema(BaseModel):
    topic_name: str
    lesson_title: str
    lesson_description: str
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    lesson_type: str = "theory"  # theory, practice, mixed
    include_examples: bool = True
    include_exercises: bool = True
    max_sections: int = 10
