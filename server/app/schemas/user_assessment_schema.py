from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class UserAssessmentBase(BaseModel):
    """Base schema cho UserAssessment"""

    strengths: Optional[Dict] = Field(None, description="Điểm mạnh của người dùng")
    weaknesses: Optional[Dict] = Field(None, description="Điểm yếu của người dùng")
    recommendations: Optional[Dict] = Field(None, description="Khuyến nghị cải thiện")
    skill_levels: Optional[Dict] = Field(
        None, description="Mức độ kỹ năng theo từng chủ đề"
    )
    learning_path: Optional[Dict] = Field(
        None, description="Lộ trình học tập được đề xuất"
    )
    overall_score: Optional[float] = Field(None, description="Điểm số tổng quan")
    proficiency_level: Optional[str] = Field(None, description="Mức độ thành thạo")
    analysis_summary: Optional[str] = Field(None, description="Tóm tắt phân tích")
    raw_analysis: Optional[Dict] = Field(
        None, description="Dữ liệu phân tích thô từ agent"
    )


class UserAssessmentCreate(UserAssessmentBase):
    """Schema để tạo UserAssessment mới"""

    user_id: int = Field(description="ID của người dùng")
    test_session_id: str = Field(description="ID của phiên thi")
    course_id: Optional[int] = Field(None, description="ID của khóa học")


class UserAssessmentUpdate(UserAssessmentBase):
    """Schema để cập nhật UserAssessment"""

    pass


class UserAssessmentResponse(UserAssessmentBase):
    """Schema cho response UserAssessment"""

    id: int
    user_id: int
    test_session_id: str
    course_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentAnalysisRequest(BaseModel):
    """Schema cho request phân tích đánh giá"""

    test_session_id: str = Field(description="ID của phiên thi")
    user_id: int = Field(description="ID của người dùng")
    course_id: Optional[int] = Field(None, description="ID của khóa học")


class WeaknessAnalysisResult(BaseModel):
    """Schema cho kết quả phân tích điểm yếu"""

    weak_topics: List[str] = Field(description="Các chủ đề yếu")
    weak_skills: List[str] = Field(description="Các kỹ năng yếu")
    difficulty_level: str = Field(description="Mức độ khó phù hợp")
    recommended_actions: List[str] = Field(description="Hành động được khuyến nghị")
    study_priority: List[str] = Field(description="Ưu tiên học tập")


class StrengthAnalysisResult(BaseModel):
    """Schema cho kết quả phân tích điểm mạnh"""

    strong_topics: List[str] = Field(description="Các chủ đề mạnh")
    strong_skills: List[str] = Field(description="Các kỹ năng mạnh")
    mastery_level: str = Field(description="Mức độ thành thạo")
    advanced_topics: List[str] = Field(description="Chủ đề nâng cao có thể học")
