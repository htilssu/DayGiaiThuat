from typing import List, Optional
from pydantic import BaseModel, Field


class GetExerciseSchema(BaseModel):
    lesson_id: int
    session_id: str
    difficulty: Optional[str] = None


class TestCase(BaseModel):
    input: str = Field(..., description="Dữ liệu đầu vào cho trường hợp thử nghiệm.")
    expectedOutput: str = Field(..., description="Kết quả đầu ra mong đợi.")
    explain: Optional[str] = Field(None, description="Giải thích cho trường hợp thử nghiệm.")


class ExerciseDetail(BaseModel):
    """
    Mô tả chi tiết một bài tập giải thuật được tạo ra.

    Attributes:
        title (str): Tiêu đề của bài toán.
        description (str): Mô tả chi tiết về bài toán.
        category (Optional[str]): Danh mục bài toán.
        difficulty (str): Độ khó của bài toán (Beginner/Intermediate/Advanced).
        estimated_time (Optional[str]): Thời gian ước tính hoàn thành.
        completion_rate (Optional[int]): Tỉ lệ hoàn thành (%).
        completed (Optional[bool]): Đã hoàn thành hay chưa.
        content (Optional[str]): Nội dung chi tiết (Markdown).
        code_template (Optional[str]): Mẫu code khởi đầu.
        testCases (List[TestCase]): Danh sách các trường hợp thử nghiệm (tối thiểu 3).
    """

    title: str = Field(..., description="Tiêu đề của bài toán.")
    description: str = Field(..., description="Mô tả chi tiết về bài toán.")
    category: Optional[str] = Field(None, description="Danh mục bài toán")
    difficulty: str = Field(..., description="Độ khó của bài toán. bằng tiếng anh")
    estimated_time: Optional[str] = Field(None, description="Thời gian ước tính hoàn thành")
    completion_rate: Optional[int] = Field(None, description="Tỉ lệ hoàn thành (%)")
    completed: Optional[bool] = Field(None, description="Trạng thái hoàn thành")
    content: Optional[str] = Field(None, description="Nội dung chi tiết (Markdown)")
    code_template: Optional[str] = Field(None, description="Mẫu code khởi đầu")
    testCases: List[TestCase] = Field(
        min_length=3,
        description="Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.",
    )


class UpdateExerciseSchema(BaseModel):
    lesson_id: Optional[int] = None
    session_id: Optional[str] = None
    difficulty: Optional[str] = None


class CreateExerciseSchema(BaseModel):
    lesson_id: int
    session_id: str
    difficulty: str
    topic_id: int


class ExerciseResponse(BaseModel):
    """
    Schema cho response khi truy vấn thông tin bài tập

    Attributes:
        id: ID của bài tập
        title: Tiêu đề bài tập
        description: Mô tả chi tiết về bài tập
        category: Danh mục bài tập
        difficulty: Độ khó của bài tập
        estimated_time: Thời gian ước tính
        completion_rate: Tỉ lệ hoàn thành
        completed: Trạng thái hoàn thành
        content: Nội dung chi tiết
        code_template: Mẫu code
        lesson_id: ID của bài học liên quan
    """
    id: int = Field(..., description="ID của bài tập")
    title: str = Field(..., description="Tiêu đề bài tập")
    description: str = Field(..., description="Mô tả chi tiết về bài tập")
    category: Optional[str] = Field(None, description="Danh mục bài tập")
    difficulty: str = Field(..., description="Độ khó của bài tập")
    estimated_time: Optional[str] = Field(None, description="Thời gian ước tính")
    completion_rate: Optional[int] = Field(None, description="Tỉ lệ hoàn thành")
    completed: Optional[bool] = Field(None, description="Trạng thái hoàn thành")
    content: Optional[str] = Field(None, description="Nội dung chi tiết")
    code_template: Optional[str] = Field(None, description="Mẫu code")
    lesson_id: int = Field(..., description="ID của bài học liên quan")

    class Config:
        from_attributes = True


class CodeSubmissionRequest(BaseModel):
    code: str = Field(..., description="User's submitted code")
    language: str = Field(..., description="Programming language (e.g., python, javascript, java, cpp, etc.)")


class TestCaseResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str
    passed: bool
    error: str | None = None


class CodeSubmissionResponse(BaseModel):
    results: list[TestCaseResult]
    all_passed: bool


class ExerciseUpdate(BaseModel):
    """Schema cập nhật bài tập (partial update)."""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_time: Optional[str] = None
    completion_rate: Optional[int] = None
    completed: Optional[bool] = None
    content: Optional[str] = None
    code_template: Optional[str] = None
