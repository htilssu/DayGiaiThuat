from typing import List
from pydantic import BaseModel, Field


class TopicAssessmentResponse(BaseModel):
    """Response schema cho đánh giá từng chủ đề"""

    topic_id: int = Field(description="ID của chủ đề")
    topic_name: str = Field(description="Tên chủ đề")
    score_percentage: float = Field(description="Điểm số phần trăm cho chủ đề này")
    level: str = Field(
        description="Mức độ hiện tại", enum=["weak", "fair", "good", "excellent"]
    )
    strengths: List[str] = Field(description="Điểm mạnh trong chủ đề này")
    weaknesses: List[str] = Field(description="Điểm yếu cần cải thiện")
    recommendations: List[str] = Field(description="Gợi ý cải thiện cụ thể")


class LearningPathItemResponse(BaseModel):
    """Response schema cho một mục trong lộ trình học tập"""

    topic_id: int = Field(description="ID của chủ đề")
    topic_name: str = Field(description="Tên chủ đề")
    order: int = Field(description="Thứ tự học (1, 2, 3...)")
    priority: str = Field(description="Mức độ ưu tiên", enum=["high", "medium", "low"])
    estimated_hours: int = Field(description="Thời gian ước tính để hoàn thành (giờ)")
    reason: str = Field(description="Lý do sắp xếp thứ tự này")
    suggested_difficulty: str = Field(
        description="Mức độ khó đề xuất", enum=["easy", "medium", "hard"]
    )


class AssessmentResultResponse(BaseModel):
    """Response schema cho kết quả đánh giá toàn diện"""

    test_session_id: str = Field(description="ID phiên làm bài")
    course_id: int = Field(description="ID khóa học")
    overall_score: float = Field(description="Điểm tổng thể (0-100)")
    overall_level: str = Field(
        description="Trình độ tổng thể", enum=["beginner", "intermediate", "advanced"]
    )

    # Đánh giá chi tiết theo chủ đề
    topic_assessments: List[TopicAssessmentResponse] = Field(
        description="Đánh giá chi tiết từng chủ đề"
    )

    # Lộ trình học tập được đề xuất
    learning_path: List[LearningPathItemResponse] = Field(
        description="Lộ trình học tập được sắp xếp"
    )

    # Nhận xét và gợi ý tổng thể
    general_feedback: str = Field(description="Nhận xét tổng thể về khả năng học sinh")
    study_recommendations: List[str] = Field(description="Gợi ý phương pháp học tập")
    next_steps: List[str] = Field(description="Các bước tiếp theo nên thực hiện")

    class Config:
        from_attributes = True


class AssessmentRequest(BaseModel):
    """Request schema cho đánh giá trình độ"""

    test_session_id: str = Field(description="ID phiên làm bài kiểm tra đã hoàn thành")

    class Config:
        from_attributes = True
