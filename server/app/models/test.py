from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"))

    topic: Mapped["Topic"] = relationship(back_populates="tests")
