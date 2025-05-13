
from pydantic import BaseModel


class GetExerciseSchema(BaseModel):
    topic: str
    session_id: str

