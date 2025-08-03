from typing import List, Literal
from pydantic import BaseModel, Field


class AgentAssessmentSchema(BaseModel):
    strengths: List[str] = Field(description="Điểm mạnh")
    weaknesses: List[str] = Field(description="Điểm yếu")
    recommendations: List[str] = Field(description="Khuyến nghị cải thiện")

    class Config:
        from_attributes = True


ASSESSMENT_TYPE = Literal["test", "topic", "overview_exercise"]

class AssessmentResult(BaseModel):
    type: ASSESSMENT_TYPE