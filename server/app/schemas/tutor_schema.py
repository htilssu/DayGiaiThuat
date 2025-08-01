from pydantic import BaseModel
from typing import Optional


class AskTutorSchema(BaseModel):
    """
    Schema cho việc gửi yêu cầu hỏi gia sư
    """

    type: str = "lesson"
    question: str
    session_id: Optional[str] = None
    context_id: Optional[str] = None


class TutorResponseSchema(BaseModel):
    """
    Schema cho phản hồi từ gia sư
    """

    session_id: str
    message: str
    type: str = "lesson"

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
