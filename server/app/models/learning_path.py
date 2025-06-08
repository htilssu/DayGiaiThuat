from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base


class LearningPath(Base):
    """
    Model đại diện cho lộ trình học tập của người dùng

    Attributes:
        id (int): ID của lộ trình, là primary key
        name (str): Tên lộ trình học tập
        created_at (datetime): Thời điểm tạo lộ trình
        updated_at (datetime): Thời điểm cập nhật gần nhất
        user_id (int): ID của người dùng sở hữu lộ trình
        path (dict): Dữ liệu lộ trình dạng JSON

    Relationships:
        user (User): Người dùng sở hữu lộ trình (many-to-one)
    """

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    path: Mapped[dict] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="learning_paths")
