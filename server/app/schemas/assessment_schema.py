from typing import List, Literal, Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentAssessmentSchema(BaseModel):
    skill_name: str = Field(description="Ten skill duoc danh gia")
    weaknesses: List[str] = Field(
        description="Cac diem yeu cu the cua user trong skill nay"
    )
    weakness_analysis: str = Field(description="Phan tich chi tiet ve cac diem yeu")
    improvement_suggestions: List[str] = Field(
        description="Goi y cu the de cai thien diem yeu"
    )
    current_level: str = Field(description="Muc do hien tai cua user trong skill")
    weakness_severity: str = Field(
        description="Muc do nghiem trong cua diem yeu (Low/Medium/High)"
    )

    class Config:
        from_attributes = True


ASSESSMENT_TYPE = Literal["test", "topic", "overview_exercise"]


class AssessmentResult(BaseModel):
    type: ASSESSMENT_TYPE
    skill_name: str = Field(description="Ten skill duoc danh gia")
    weaknesses: List[str] = Field(
        default_factory=list, description="Cac diem yeu cu the"
    )
    weakness_analysis: Optional[str] = Field(
        default=None, description="Phan tich chi tiet diem yeu"
    )
    improvement_suggestions: Optional[List[str]] = Field(
        default=None, description="Goi y cai thien"
    )
    current_level: Optional[str] = Field(default=None, description="Muc do hien tai")
    weakness_severity: Optional[str] = Field(
        default=None, description="Muc do nghiem trong diem yeu"
    )
    raw_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Du lieu phan tich goc"
    )

    class Config:
        from_attributes = True
