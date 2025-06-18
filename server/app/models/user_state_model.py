from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.database import Base


class UserState(Base):
    """
    Model đại diện cho bảng user_states trong database để lưu trữ trạng thái hiện tại của người dùng

    Attributes:
        id (int): ID của trạng thái, là primary key
        user_id (int): ID của người dùng, là foreign key tới bảng users
        last_active (DateTime): Thời điểm hoạt động gần nhất của người dùng
        current_course_id (int): ID của khóa học đang học (nếu có)
        current_lesson_id (int): ID của bài học đang học (nếu có)
        streak_last_date (DateTime): Ngày gần nhất người dùng duy trì streak
        streak_count (int): Số ngày streak hiện tại
        total_points (int): Tổng số điểm tích lũy
        level (int): Cấp độ hiện tại của người dùng
        xp_to_next_level (int): Số điểm kinh nghiệm cần để lên cấp tiếp theo
        daily_goal (int): Mục tiêu học tập hàng ngày (tính bằng phút)
        daily_progress (int): Tiến độ học tập hôm nay (tính bằng phút)
        completed_exercises (int): Số bài tập đã hoàn thành
        completed_courses (int): Số khóa học đã hoàn thành
        problems_solved (int): Số bài tập thuật toán đã giải
        created_at (DateTime): Thời điểm tạo trạng thái
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """

    __tablename__ = "user_states"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    current_course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=True
    )
    current_lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lessons.id"), nullable=True
    )
    streak_last_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Các trường thống kê được chuyển từ stats của User
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp_to_next_level: Mapped[int] = mapped_column(Integer, default=100)
    daily_goal: Mapped[int] = mapped_column(Integer, default=30)  # 30 phút học mỗi ngày
    daily_progress: Mapped[int] = mapped_column(Integer, default=0)
    completed_exercises: Mapped[int] = mapped_column(Integer, default=0)
    completed_courses: Mapped[int] = mapped_column(Integer, default=0)
    problems_solved: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship với các bảng khác
    user: Mapped["User"] = relationship(back_populates="state")
    current_course: Mapped["Course"] = relationship(back_populates="user_states")
    current_lesson: Mapped["Lesson"] = relationship()
