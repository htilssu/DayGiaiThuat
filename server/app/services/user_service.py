import random
from functools import lru_cache
from datetime import datetime
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from app.utils.string import remove_vi_accents
from app.database.database import get_async_db

from app.models.user_model import User
from app.models.user_state_model import UserState
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

        # Tạo UserState cho user mới
        user_state = UserState(
            user_id=new_user.id,
            total_points=0,
            level=1,
            xp_to_next_level=100,
            daily_goal=30,
            daily_progress=0,
            completed_exercises=0,
            completed_courses=0,
            problems_solved=0,
        )
        self.db.add(user_state)
        await self.db.commit()

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

        # Lấy hoặc tạo UserState
        user_state_result = await self.db.execute(
            select(UserState).where(UserState.user_id == user_id)
        )
        user_state = user_state_result.scalar_one_or_none()

        if not user_state:
            user_state = UserState(user_id=user_id)
            self.db.add(user_state)

        # Cập nhật thống kê dựa trên loại hoạt động
        activity_type = activity_data.get("type")

        if activity_type == "exercise":
            user_state.completed_exercises += 1
            user_state.total_points += 10

            # Kiểm tra nếu là bài tập code
            if "code" in activity_data.get("tags", []):
                user_state.problems_solved += 1

        elif activity_type == "course":
            if activity_data.get("completed"):
                user_state.completed_courses += 1
                user_state.total_points += 50

        # Cập nhật level nếu cần
        await self._update_level(user_state)

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

        # TODO: Implement badge system with UserBadge model
        # For now, just update the user timestamp
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

    async def _update_level(self, user_state: UserState) -> None:
        """
        Cập nhật level của người dùng dựa trên điểm số

        Args:
            user_state (UserState): Trạng thái người dùng
        """
        # Công thức tính level: level = 1 + floor(sqrt(points / 100))
        new_level = 1 + int((user_state.total_points / 100) ** 0.5)

        if new_level > user_state.level:
            user_state.level = new_level
            user_state.xp_to_next_level = (
                new_level + 1
            ) ** 2 * 100 - user_state.total_points

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

        # Lấy UserState
        user_state_result = await self.db.execute(
            select(UserState).where(UserState.user_id == user_id)
        )
        user_state = user_state_result.scalar_one_or_none()

        if not user_state:
            user_state = UserState(user_id=user_id)
            self.db.add(user_state)

        # Kiểm tra ngày cuối cùng đã hoạt động
        today = datetime.utcnow().date()

        if user_state.streak_last_date:
            # Tính số ngày giữa lần hoạt động cuối và hiện tại
            days_diff = (today - user_state.streak_last_date.date()).days

            if days_diff == 1:
                # Hoạt động liên tiếp, tăng streak
                user_state.streak_count += 1
            elif days_diff > 1:
                # Mất streak, đặt lại
                user_state.streak_count = 1
            # Nếu days_diff = 0, giữ nguyên streak
        else:
            # Lần đầu hoạt động
            user_state.streak_count = 1

        # Cập nhật ngày hoạt động
        user_state.streak_last_date = datetime.utcnow()
        user_state.last_active = datetime.utcnow()

        # Lưu lại thống kê
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)

        # Kiểm tra và cấp huy hiệu (nếu cần)
        await self._check_streak_badge(user)

        return user

    async def _check_streak_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến streak

        Args:
            user (User): Thông tin người dùng
        """
        user_state_result = await self.db.execute(
            select(UserState).where(UserState.user_id == user.id)
        )
        user_state = user_state_result.scalar_one_or_none()

        if not user_state:
            return

        streak_count = user_state.streak_count

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
            if streak_count >= badge_data["threshold"]:
                # Xóa trường threshold trước khi thêm huy hiệu
                badge_info = {k: v for k, v in badge_data.items() if k != "threshold"}
                await self.add_badge(user.id, badge_info)

    async def _check_level_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến level

        Args:
            user (User): Thông tin người dùng
        """
        user_state_result = await self.db.execute(
            select(UserState).where(UserState.user_id == user.id)
        )
        user_state = user_state_result.scalar_one_or_none()

        if not user_state:
            return

        level = user_state.level

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
        # TODO: Implement other badge checks
        # await self._check_problem_solved_badge(user)
        # await self._check_account_age_badge(user)

        return user

    async def _random_username(self, first_name: str, last_name: str) -> str:
        fullname = f"{first_name.lower()}{last_name.lower()}"
        username = f"{remove_vi_accents(fullname)}{random.randint(999, 99999)}"
        while await self.get_user_by_username(username):
            username = f"{remove_vi_accents(fullname)}{random.randint(999, 99999)}"
        return username.replace(" ", "")

    # Admin User Management Methods

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lấy danh sách tất cả người dùng với phân trang

        Args:
            skip (int): Số bản ghi bỏ qua
            limit (int): Số bản ghi trả về

        Returns:
            List[User]: Danh sách người dùng
        """
        from sqlalchemy import select

        result = await self.db.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_user_admin_info(
        self,
        user_id: int,
        is_admin: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """
        Cập nhật thông tin admin của người dùng

        Args:
            user_id (int): ID của người dùng
            is_admin (bool, optional): Quyền admin
            is_active (bool, optional): Trạng thái hoạt động

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if is_admin is not None:
            user.is_admin = is_admin
        if is_active is not None:
            user.is_active = is_active

        user.updated_at = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_admin(
        self, user_id: int, user_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Cập nhật thông tin người dùng (admin)

        Args:
            user_id (int): ID của người dùng
            user_data (Dict[str, Any]): Dữ liệu cập nhật

        Returns:
            Optional[User]: Thông tin người dùng đã cập nhật hoặc None
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Cập nhật các trường có thể thay đổi
        if user_data.get("email") is not None:
            user.email = user_data["email"]
        if user_data.get("username") is not None:
            user.username = user_data["username"]
        if user_data.get("first_name") is not None:
            user.first_name = user_data["first_name"]
        if user_data.get("last_name") is not None:
            user.last_name = user_data["last_name"]
        if user_data.get("is_admin") is not None:
            user.is_admin = user_data["is_admin"]
        if user_data.get("is_active") is not None:
            user.is_active = user_data["is_active"]
        if user_data.get("bio") is not None:
            user.bio = user_data["bio"]
        if user_data.get("avatar_url") is not None:
            user.avatar = user_data["avatar_url"]

        user.updated_at = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Vô hiệu hóa người dùng

        Args:
            user_id (int): ID của người dùng

        Returns:
            Optional[User]: Thông tin người dùng đã vô hiệu hóa hoặc None
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def activate_user(self, user_id: int) -> Optional[User]:
        """
        Kích hoạt người dùng

        Args:
            user_id (int): ID của người dùng

        Returns:
            Optional[User]: Thông tin người dùng đã kích hoạt hoặc None
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int, force: bool = False) -> bool:
        """
        Xóa người dùng

        Args:
            user_id (int): ID của người dùng
            force (bool): Bắt buộc xóa không kiểm tra dependencies

        Returns:
            bool: True nếu xóa thành công, False nếu không
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        if not force:
            # Kiểm tra dependencies trước khi xóa
            # TODO: Implement dependency checking
            # Ví dụ: kiểm tra xem user có đang tham gia khóa học nào không
            pass

        try:
            await self.db.delete(user)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
