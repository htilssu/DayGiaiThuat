from typing import List, Optional
from pydantic import BaseModel, Field


class GetExerciseSchema(BaseModel):
    lesson_id: int
    session_id: str
    difficulty: Optional[str] = None


class TestCase(BaseModel):
    """
    Mô tả một trường hợp thử nghiệm cho bài toán giải thuật.

    Attributes:
        input_data (str): Dữ liệu đầu vào cho trường hợp thử nghiệm. Alias là "input".
        output_data (str): Kết quả đầu ra mong đợi. Alias là "output".
        explain (str): Giải thích cho trường hợp thử nghiệm.
    """

    input_data: str = Field(
        ..., alias="input", description="Dữ liệu đầu vào cho trường hợp thử nghiệm."
    )
    output_data: str = Field(
        ..., alias="output", description="Kết quả đầu ra mong đợi."
    )
    explain: str = Field(..., description="Giải thích cho trường hợp thử nghiệm.")


class ExerciseDetail(BaseModel):
    """
    Mô tả chi tiết một bài tập giải thuật được tạo ra.

    Attributes:
        name (str): Tên của bài toán.
        description (str): Mô tả chi tiết về bài toán.
        constraints (Optional[str]): Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).
        suggest (Optional[str]): Gợi ý để giải bài toán.
        case (List[TestCase]): Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.
    """

    name: str = Field(..., description="Tên của bài toán.")
    description: str = Field(..., description="Mô tả chi tiết về bài toán.")
    difficulty: str = Field(..., description="Độ khó của bài toán. bằng tiếng anh")
    constraint: Optional[str] = Field(
        None, description="Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào)."
    )
    suggest: Optional[str] = Field(None, description="Gợi ý để giải bài toán.")
    case: List[TestCase] = Field(
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
        name: Tên bài tập
        description: Mô tả chi tiết về bài tập
        difficulty: Độ khó của bài tập
        constraint: Các ràng buộc hoặc yêu cầu của bài tập
        suggest: Gợi ý để giải bài tập
        lesson_id: ID của bài học liên quan
    """
    id: int = Field(..., description="ID của bài tập")
    name: str = Field(..., description="Tên bài tập")
    description: str = Field(..., description="Mô tả chi tiết về bài tập")
    difficulty: str = Field(..., description="Độ khó của bài tập")
    constraint: Optional[str] = Field(None, description="Các ràng buộc hoặc yêu cầu của bài tập")
    suggest: Optional[str] = Field(None, description="Gợi ý để giải bài tập")
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
