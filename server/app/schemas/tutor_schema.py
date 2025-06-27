from pydantic import BaseModel


class AskTutorSchema(BaseModel):
    """
    Schema cho việc gửi yêu cầu hỏi gia sư
    """

    question: str
    session_id: str
