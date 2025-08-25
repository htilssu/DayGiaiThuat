from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.topic_model import Topic


class Skill(Base):
    """
    Model đại diện cho kỹ năng (skill) trong database

    Attributes:
        id (int): ID của kỹ năng, là primary key
        name (str): Tên kỹ năng
        description (str): Mô tả chi tiết về kỹ năng
        topic_id (int): ID của topic mà kỹ năng này thuộc về
        created_at (DateTime): Thời điểm tạo kỹ năng
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="skills")
