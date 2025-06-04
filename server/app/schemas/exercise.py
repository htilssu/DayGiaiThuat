from typing import Optional
from pydantic import BaseModel


class GetExerciseSchema(BaseModel):
    topic: str
    session_id: str
    difficulty: Optional[str] = None
