from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class Exercise(Base):
    """
    Model đại diện cho bảng exercises trong database

    Attributes:
        id (int): ID của bài tập, là primary key
        name (str): Tên bài tập
        description (str): Mô tả chi tiết về bài tập
        category (str): Phân loại bài tập
        difficulty (str): Độ khó của bài tập
        constraint (str): Các ràng buộc hoặc yêu cầu của bài tập
        duration (int): Thời gian làm bài (tính bằng phút)
        sets (int): Số lượng bộ bài tập
        topic_id (int): ID của chủ đề liên quan, foreign key đến bảng topics

    Relationships:
        topic (Topic): Chủ đề liên quan đến bài tập (many-to-one)
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    constraint: Mapped[str] = mapped_column(String)
    duration: Mapped[int] = mapped_column(Integer)  # in minutes
    sets: Mapped[int] = mapped_column(Integer)  # number of sets for the exercise
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))

    topic: Mapped["Topic"] = relationship(back_populates="exercises")

    class Config:
        orm_mode = True
