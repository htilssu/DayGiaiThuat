import random
from functools import lru_cache
from datetime import datetime
from sqlalchemy import select
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from app.utils.string import remove_vi_accents
from app.database.database import get_async_db

from app.models.user_model import User
from app.schemas.auth_schema import UserRegister
from app.schemas.user_profile_schema import UserUpdate


@lru_cache(maxsize=1)
def get_password_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_service(db: AsyncSession = Depends(get_async_db)):
    return UserService(db)


class UserService:
    """
    Service xử lý logic liên quan đến User
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Lấy thông tin người dùng theo ID

        Args:
            user_id (int): ID của người dùng

        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        user = await self.db.execute(select(User).where(User.id == user_id))
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Lấy thông tin người dùng theo email

        Args:
            email (str): Email của người dùng

        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Lấy thông tin người dùng theo username

        Args:
            username (str): Username của người dùng

        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Kiểm tra mật khẩu

        Args:
            plain_password (str): Mật khẩu gốc
            hashed_password (str): Mật khẩu đã mã hóa

        Returns:
            bool: True nếu mật khẩu đúng, ngược lại là False
        """
        pwd_context = get_password_context()
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Mã hóa mật khẩu

        Args:
            password (str): Mật khẩu gốc

        Returns:
            str: Mật khẩu đã mã hóa
        """
        pwd_context = get_password_context()
        return pwd_context.hash(password)

    async def create_user(self, user_data: UserRegister) -> User:
        """
        Tạo người dùng mới

        Args:
            user_data (UserRegister): Thông tin người dùng mới

        Returns:
            User: Người dùng đã được tạo

        Raises:
            HTTPException: Nếu email hoặc username đã tồn tại
        """
        # Kiểm tra email đã tồn tại chưa
        db_user = await self.get_user_by_email(user_data.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được sử dụng"
            )

        # random username
        username = await self._random_username(
            user_data.first_name, user_data.last_name
        )

        # Mã hóa mật khẩu
        hashed_password = self.get_password_hash(user_data.password)

        new_user = User(
            email=user_data.email,
            username=username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar="/avatars/default.png",
        )

        # Lưu vào database
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Cập nhật mật khẩu cho người dùng

        Args:
            user_id (int): ID của người dùng
            new_password (str): Mật khẩu mới

        Returns:
            bool: True nếu cập nhật thành công, ngược lại là False
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        # Mã hóa mật khẩu mới
        hashed_password = self.get_password_hash(new_password)

        # Cập nhật mật khẩu
        user.hashed_password = hashed_password
        user.updated_at = datetime.utcnow()

        # Lưu vào database
        await self.db.commit()

        return True

    async def update_user_profile(
        self, user_id: int, profile_data: UserUpdate
    ) -> Optional[User]:
        """
        Cập nhật thông tin profile của người dùng

        Args:
            user_id (int): ID của người dùng
            profile_data (UserUpdate): Thông tin profile mới

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Cập nhật thông tin
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        user.updated_at = datetime.utcnow()

        # Lưu vào database
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def add_activity(
        self, user_id: int, activity_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Thêm hoạt động mới vào profile của người dùng

        Args:
            user_id (int): ID của người dùng
            activity_data (Dict[str, Any]): Thông tin hoạt động mới

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Tạo chuỗi định dạng ngày tháng
        activity_date = datetime.now().strftime("%d/%m/%Y")

        # Tạo hoạt động mới
        activity = {
            "type": activity_data.get("type"),
            "name": activity_data.get("name"),
            "date": activity_date,
        }

        # Thêm thông tin tùy chọn
        if "score" in activity_data:
            activity["score"] = activity_data["score"]
        if "progress" in activity_data:
            activity["progress"] = activity_data["progress"]

        # Cập nhật thống kê
        await self._update_stats_after_activity(user, activity_data)

        # Lưu vào database
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def add_badge(
        self, user_id: int, badge_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Thêm huy hiệu mới vào profile của người dùng

        Args:
            user_id (int): ID của người dùng
            badge_data (Dict[str, Any]): Thông tin huy hiệu mới

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        badges = user.badges if user.badges else []

        # Kiểm tra huy hiệu đã tồn tại chưa
        badge_id = badge_data.get("id")
        for i, badge in enumerate(badges):
            if badge.get("id") == badge_id:
                # Cập nhật trạng thái huy hiệu đã có
                badges[i]["unlocked"] = badge_data.get("unlocked", True)
                user.updated_at = datetime.now()
                await self.db.commit()
                await self.db.refresh(user)
                return user

        # Thêm huy hiệu mới
        badge = {
            "id": badge_id,
            "name": badge_data.get("name"),
            "icon": badge_data.get("icon"),
            "description": badge_data.get("description"),
            "unlocked": badge_data.get("unlocked", True),
        }

        badges.append(badge)

        # Lưu vào database
        user.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_learning_progress(
        self, user_id: int, progress_data: Dict[str, int]
    ) -> Optional[User]:
        """
        Cập nhật tiến độ học tập của người dùng

        Args:
            user_id (int): ID của người dùng
            progress_data (Dict[str, int]): Thông tin tiến độ học tập mới

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        # TODO: Cập nhật tiến độ học tập
        # Lưu vào database
        user.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_course_progress(
        self, user_id: int, course_id: str, progress: int
    ) -> Optional[User]:
        """
        Cập nhật tiến độ khóa học

        Args:
            user_id (int): ID của người dùng
            course_id (str): ID của khóa học
            progress (int): Tiến độ mới (0-100%)

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # TODO: Cập nhật tiến độ khóa học
        return None

    async def _update_stats_after_activity(
        self, user: User, activity_data: Dict[str, Any]
    ) -> None:
        """
        Cập nhật thống kê sau khi có hoạt động mới

        Args:
            user (User): Thông tin người dùng
            activity_data (Dict[str, Any]): Thông tin hoạt động mới
        """
        stats = user.stats if user.stats else {}
        activity_type = activity_data.get("type")

        if activity_type == "exercise":
            # Bài tập hoàn thành
            stats["completed_exercises"] = stats.get("completed_exercises", 0) + 1
            stats["total_points"] = stats.get("total_points", 0) + 10

            # Kiểm tra nếu là bài tập code
            if "code" in activity_data.get("tags", []):
                stats["problems_solved"] = stats.get("problems_solved", 0) + 1

        elif activity_type == "course":
            # Khóa học hoàn thành
            if activity_data.get("completed"):
                stats["completed_courses"] = stats.get("completed_courses", 0) + 1
                stats["total_points"] = stats.get("total_points", 0) + 50

        # Cập nhật level nếu cần
        await self._update_level(user, stats)

        # Lưu lại thống kê
        user.stats = stats

    async def _update_level(self, user: User, stats: Dict[str, Any]) -> None:
        """
        Cập nhật level của người dùng dựa trên điểm số

        Args:
            user (User): Thông tin người dùng
            stats (Dict[str, Any]): Thống kê người dùng
        """
        total_points = stats.get("total_points", 0)
        current_level = stats.get("level", 1)

        # Công thức tính level: level = 1 + floor(sqrt(points / 100))
        new_level = 1 + int((total_points / 100) ** 0.5)

        if new_level > current_level:
            stats["level"] = new_level

            # Tạo hoạt động lên cấp
            await self.add_activity(
                user.id,
                {"type": "level_up", "name": f"Lên cấp {new_level}", "completed": True},
            )

            # Kiểm tra và cấp huy hiệu (nếu cần)
            await self._check_level_badge(user)

    async def update_streak(self, user_id: int) -> Optional[User]:
        """
        Cập nhật chuỗi ngày hoạt động liên tiếp (streak)

        Args:
            user_id (int): ID của người dùng

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Lấy thống kê hiện tại
        stats = user.stats if user.stats else {}

        # Kiểm tra ngày cuối cùng đã hoạt động
        last_active_date = stats.get("last_active_date")
        today = datetime.utcnow().date()

        if last_active_date:
            # Chuyển định dạng ngày
            if isinstance(last_active_date, str):
                last_active_date = datetime.strptime(
                    last_active_date, "%Y-%m-%d"
                ).date()

            # Tính số ngày giữa lần hoạt động cuối và hiện tại
            days_diff = (today - last_active_date).days

            if days_diff == 1:
                # Hoạt động liên tiếp, tăng streak
                stats["streak_days"] = stats.get("streak_days", 0) + 1
            elif days_diff > 1:
                # Mất streak, đặt lại
                stats["streak_days"] = 1
            # Nếu days_diff = 0, giữ nguyên streak
        else:
            # Lần đầu hoạt động
            stats["streak_days"] = 1

        # Cập nhật ngày hoạt động
        stats["last_active_date"] = today.isoformat()

        # Lưu lại thống kê
        user.stats = stats
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        # Kiểm tra và cấp huy hiệu (nếu cần)
        await self._check_streak_badge(user)

        return user

    async def _check_streak_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến streak

        Args:
            user (User): Thông tin người dùng
        """
        stats = user.stats if user.stats else {}
        streak_days = stats.get("streak_days", 0)

        # Danh sách huy hiệu streak
        streak_badges = [
            {
                "id": 10,
                "name": "Chăm chỉ",
                "icon": "🔥",
                "description": "Hoạt động liên tục 7 ngày",
                "threshold": 7,
            },
            {
                "id": 11,
                "name": "Kiên trì",
                "icon": "⚡",
                "description": "Hoạt động liên tục 30 ngày",
                "threshold": 30,
            },
            {
                "id": 12,
                "name": "Siêu nhân",
                "icon": "🚀",
                "description": "Hoạt động liên tục 100 ngày",
                "threshold": 100,
            },
        ]

        # Kiểm tra từng huy hiệu
        for badge_data in streak_badges:
            if streak_days >= badge_data["threshold"]:
                # Xóa trường threshold trước khi thêm huy hiệu
                badge_info = {k: v for k, v in badge_data.items() if k != "threshold"}
                await self.add_badge(user.id, badge_info)

    async def _check_level_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến level

        Args:
            user (User): Thông tin người dùng
        """
        stats = user.stats if user.stats else {}
        level = stats.get("level", 1)

        # Danh sách huy hiệu level
        level_badges = [
            {
                "id": 20,
                "name": "Tân binh",
                "icon": "🌱",
                "description": "Đạt cấp độ 5",
                "threshold": 5,
            },
            {
                "id": 21,
                "name": "Chiến binh",
                "icon": "⚔️",
                "description": "Đạt cấp độ 10",
                "threshold": 10,
            },
            {
                "id": 22,
                "name": "Bậc thầy",
                "icon": "🏆",
                "description": "Đạt cấp độ 20",
                "threshold": 20,
            },
        ]

        # Kiểm tra từng huy hiệu
        for badge_data in level_badges:
            if level >= badge_data["threshold"]:
                # Xóa trường threshold trước khi thêm huy hiệu
                badge_info = {k: v for k, v in badge_data.items() if k != "threshold"}
                await self.add_badge(user.id, badge_info)

    async def update_badges(self, user_id: int) -> Optional[User]:
        """
        Cập nhật và kiểm tra các huy hiệu cho người dùng

        Args:
            user_id (int): ID của người dùng

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None nếu không tìm thấy
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Kiểm tra các loại huy hiệu
        await self._check_streak_badge(user)
        await self._check_level_badge(user)
        await self._check_problem_solved_badge(user)
        await self._check_account_age_badge(user)

        return user

    async def _random_username(self, first_name: str, last_name: str) -> str:
        fullname = f"{first_name.lower()}{last_name.lower()}"
        username = f"{remove_vi_accents(fullname)}{random.randint(999, 99999)}"
        while await self.get_user_by_username(username):
            username = f"{remove_vi_accents(fullname)}{random.randint(999, 99999)}"
        return username.replace(" ", "")
