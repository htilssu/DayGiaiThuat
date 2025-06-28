from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database.database import Base
from app.schemas.exercise_schema import ExerciseDetail

if TYPE_CHECKING:
    from app.models.lesson_model import Lesson


class Exercise(Base):
    """
    Model đại diện cho bảng exercises trong database

    Attributes:
        id (int): ID của bài tập, là primary key
        name (str): Tên bài tập
        description (str): Mô tả chi tiết về bài tập
        difficulty (str): Độ khó của bài tập
        constraint (str): Các ràng buộc hoặc yêu cầu của bài tập
        lesson_id (int): ID của bài học liên quan, foreign key đến bảng lessons
        suggest (str): Gợi ý để giải bài tập

    Relationships:
        lesson (Lesson): Bài học liên quan đến bài tập (one-to-one)
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    constraint: Mapped[str] = mapped_column(String, nullable=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), unique=True)
    suggest: Mapped[str] = mapped_column(String, nullable=True)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercise")

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
                - constraint (str): Các ràng buộc của bài tập (có thể None)
                - suggest (str): Gợi ý để giải bài tập (có thể None)
                - lesson_id (int): ID của bài học liên quan

        Returns:
            Exercise: Đối tượng Exercise được tạo từ dữ liệu schema
        """
        exercise = Exercise()

        # Các trường bắt buộc
        exercise.name = data.name
        exercise.description = data.description
        exercise.difficulty = data.difficulty

        # Các trường có thể None
        exercise.constraint = data.constraint or ""
        exercise.suggest = data.suggest or ""

        return exercise
