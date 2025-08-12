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
    case: Mapped[str] = mapped_column(JSON, nullable=True)

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

        return exercise
