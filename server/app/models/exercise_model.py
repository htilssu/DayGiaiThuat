from sqlalchemy import JSON, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database.database import Base
from app.schemas.exercise_schema import ExerciseDetail

if TYPE_CHECKING:
    from app.models.lesson_model import Lesson
    from app.models.exercise_test_case_model import ExerciseTestCase


class Exercise(Base):
    """
    Model đại diện cho bảng exercises trong database

    Attributes:
        id (int): ID của bài tập, là primary key
        title (str): Tiêu đề bài tập
        name (str): (Deprecated) Tên bài tập, giữ lại để tương thích ngược nếu có dữ liệu cũ
        description (str): Mô tả chi tiết về bài tập
        category (str): Danh mục bài tập
        difficulty (str): Độ khó của bài tập
        estimated_time (str): Thời gian ước tính để hoàn thành bài tập
        completion_rate (int): Tỉ lệ hoàn thành (phần trăm)
        completed (bool): Trạng thái đã hoàn thành hay chưa
        content (str): Nội dung chi tiết (Markdown)
        code_template (str): Mẫu code khởi đầu cho bài tập
        lesson_id (int): ID của bài học liên quan, foreign key đến bảng lessons

    Relationships:
        lesson (Lesson): Bài học liên quan đến bài tập (one-to-one)
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # New fields aligned with frontend `ExerciseItem`
    title: Mapped[str] = mapped_column(String)
    # Keep `name` for backward compatibility if any code still references it
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[str] = mapped_column(String)
    estimated_time: Mapped[str | None] = mapped_column(String, nullable=True)
    completion_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"), index=True, nullable=True
    )
    case: Mapped[list | None] = mapped_column(JSON, nullable=True)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercises")
    # Quan hệ tới test cases dạng quan hệ thay vì JSON `case`
    test_cases: Mapped[list["ExerciseTestCase"]] = relationship(
        "ExerciseTestCase",
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    class Config:
        from_attributes = True

    @staticmethod
    def exercise_from_schema(data: ExerciseDetail):
        """
        Tạo đối tượng Exercise từ dữ liệu schema

        Args:
            **kwargs: Các tham số được truyền vào từ schema, bao gồm:
                - name (str): Tên bài tập
                - description (str): Mô tả chi tiết về bài tập
                - difficulty (str): Độ khó của bài tập
                - lesson_id (int): ID của bài học liên quan

        Returns:
            Exercise: Đối tượng Exercise được tạo từ dữ liệu schema
        """
        exercise = Exercise()

        # Các trường bắt buộc / ưu tiên title, fallback sang name nếu có
        exercise.title = getattr(data, "title", None) or getattr(data, "name", None) or ""
        # Ghi lại `name` để tương thích nếu nơi khác còn dùng
        exercise.name = getattr(data, "name", None) or exercise.title
        exercise.description = data.description
        exercise.difficulty = data.difficulty

        # Các trường mở rộng có thể None
        exercise.category = getattr(data, "category", None)
        exercise.estimated_time = getattr(data, "estimated_time", None)
        exercise.completion_rate = getattr(data, "completion_rate", None)
        exercise.completed = getattr(data, "completed", None)
        exercise.content = getattr(data, "content", None)
        exercise.code_template = getattr(data, "code_template", None)

        # Convert testCases to case field for backward compatibility
        if hasattr(data, "testCases") and data.testCases:
            # Convert the new format to the old format for backward compatibility
            case_data = []
            for test_case in data.testCases:
                case_data.append({
                    "input_data": test_case.input,
                    "output_data": test_case.expectedOutput,
                    "explain": getattr(test_case, "explain", None)
                })
            exercise.case = case_data

        return exercise

    def to_schema_format(self) -> dict:
        """
        Convert Exercise model to frontend-compatible format

        Returns:
            dict: Exercise data in frontend format with testCases array
        """
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "estimated_time": self.estimated_time,
            "completion_rate": self.completion_rate,
            "completed": self.completed,
            "content": self.content,
            "code_template": self.code_template,
            "lesson_id": self.lesson_id,
        }

        # Convert case field to testCases format for frontend
        if self.case and isinstance(self.case, list):
            test_cases = []
            for tc in self.case:
                if isinstance(tc, dict):
                    test_cases.append({
                        "input": tc.get("input_data", ""),
                        "expectedOutput": tc.get("output_data", ""),
                        "explain": tc.get("explain")
                    })
            result["testCases"] = test_cases
        else:
            result["testCases"] = []

        return result
