from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any
import random

from ..database.database import SessionLocal
from ..models.user import User
from ..schemas.auth import UserCreate
from ..schemas.user_profile import UserUpdate

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """
    Service xử lý logic liên quan đến User
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Lấy thông tin người dùng theo ID
        
        Args:
            user_id (int): ID của người dùng
            
        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Nếu user không tồn tại, trả về None
        if not user:
            return None
            
        # Kiểm tra xem user có dữ liệu stats và learning_progress chưa, nếu chưa thì thêm vào
        if not hasattr(user, 'stats') or user.stats is None:
            user.stats = {
                "completed_exercises": 0,
                "completed_courses": 0,
                "total_points": 0,
                "streak_days": 0,
                "level": 1,
                "problems_solved": 0
            }
            
        if not hasattr(user, 'learning_progress') or user.learning_progress is None:
            user.learning_progress = {
                "algorithms": 0,
                "data_structures": 0,
                "dynamic_programming": 0
            }
            
        # Lưu lại vào database nếu có thay đổi
        self.db.commit()
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Lấy thông tin người dùng theo email
        
        Args:
            email (str): Email của người dùng
            
        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Lấy thông tin người dùng theo username
        
        Args:
            username (str): Username của người dùng
            
        Returns:
            Optional[User]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Kiểm tra mật khẩu
        
        Args:
            plain_password (str): Mật khẩu gốc
            hashed_password (str): Mật khẩu đã mã hóa
            
        Returns:
            bool: True nếu mật khẩu đúng, ngược lại là False
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Mã hóa mật khẩu
        
        Args:
            password (str): Mật khẩu gốc
            
        Returns:
            str: Mật khẩu đã mã hóa
        """
        return pwd_context.hash(password)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Tạo người dùng mới
        
        Args:
            user_data (UserCreate): Thông tin người dùng mới
            
        Returns:
            User: Người dùng đã được tạo
            
        Raises:
            HTTPException: Nếu email hoặc username đã tồn tại
        """
        # Kiểm tra email đã tồn tại chưa
        db_user = await self.get_user_by_email(user_data.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        
        # Kiểm tra username đã tồn tại chưa
        db_user = await self.get_user_by_username(user_data.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username đã được sử dụng"
            )
        
        # Mã hóa mật khẩu
        hashed_password = self.get_password_hash(user_data.password)
        
        # Tạo người dùng mới
        now = datetime.utcnow()
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=f"/avatars/default-{random.randint(1, 5)}.png",
            created_at=now,
            updated_at=now,
            stats={
                "completed_exercises": 0,
                "completed_courses": 0,
                "total_points": 0,
                "streak_days": 0,
                "level": 1,
                "problems_solved": 0
            },
            badges=[
                {
                    "id": 1,
                    "name": "Người mới",
                    "icon": "🔰",
                    "description": "Hoàn thành đăng ký tài khoản",
                    "unlocked": True
                }
            ],
            activities=[],
            learning_progress={
                "algorithms": 0,
                "data_structures": 0,
                "dynamic_programming": 0
            },
            courses=[]
        )
        
        # Lưu vào database
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
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
        self.db.commit()
        
        return True
    
    async def update_user_profile(self, user_id: int, profile_data: UserUpdate) -> Optional[User]:
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
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def add_activity(self, user_id: int, activity_data: Dict[str, Any]) -> Optional[User]:
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
        
        # Tạo ID cho hoạt động mới
        activities = user.activities if user.activities else []
        activity_id = len(activities) + 1
        
        # Tạo chuỗi định dạng ngày tháng
        activity_date = datetime.now().strftime("%d/%m/%Y")
        
        # Tạo hoạt động mới
        activity = {
            "id": activity_id,
            "type": activity_data.get("type"),
            "name": activity_data.get("name"),
            "date": activity_date
        }
        
        # Thêm thông tin tùy chọn
        if "score" in activity_data:
            activity["score"] = activity_data["score"]
        if "progress" in activity_data:
            activity["progress"] = activity_data["progress"]
        
        # Thêm hoạt động mới
        activities.append(activity)
        user.activities = activities
        
        # Cập nhật thống kê
        await self._update_stats_after_activity(user, activity_data)
        
        # Lưu vào database
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def add_badge(self, user_id: int, badge_data: Dict[str, Any]) -> Optional[User]:
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
                user.badges = badges
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
                return user
        
        # Thêm huy hiệu mới
        badge = {
            "id": badge_id,
            "name": badge_data.get("name"),
            "icon": badge_data.get("icon"),
            "description": badge_data.get("description"),
            "unlocked": badge_data.get("unlocked", True)
        }
        
        badges.append(badge)
        user.badges = badges
        
        # Lưu vào database
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def update_learning_progress(self, user_id: int, progress_data: Dict[str, int]) -> Optional[User]:
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
        
        # Cập nhật tiến độ học tập
        learning_progress = user.learning_progress if user.learning_progress else {}
        for key, value in progress_data.items():
            learning_progress[key] = value
        
        user.learning_progress = learning_progress
        
        # Lưu vào database
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def update_course_progress(self, user_id: int, course_id: str, progress: int) -> Optional[User]:
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
        
        # Lấy danh sách khóa học
        courses = user.courses if user.courses else []
        
        # Kiểm tra khóa học đã tồn tại chưa
        for i, course in enumerate(courses):
            if course.get("id") == course_id:
                # Cập nhật tiến độ
                courses[i]["progress"] = progress
                
                # Kiểm tra hoàn thành khóa học
                if progress >= 100 and courses[i].get("progress", 0) < 100:
                    # Cập nhật thống kê
                    stats = user.stats if user.stats else {}
                    stats["completed_courses"] = stats.get("completed_courses", 0) + 1
                    user.stats = stats
                
                user.courses = courses
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
                return user
        
        # Không tìm thấy khóa học, trả về None
        return None
    
    async def _update_stats_after_activity(self, user: User, activity_data: Dict[str, Any]) -> None:
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
            await self.add_activity(user.id, {
                "type": "level_up",
                "name": f"Lên cấp {new_level}",
                "completed": True
            })
            
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
                last_active_date = datetime.strptime(last_active_date, "%Y-%m-%d").date()
            
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
                "threshold": 7
            },
            {
                "id": 11,
                "name": "Kiên trì",
                "icon": "⚡",
                "description": "Hoạt động liên tục 30 ngày",
                "threshold": 30
            },
            {
                "id": 12,
                "name": "Siêu nhân",
                "icon": "🚀",
                "description": "Hoạt động liên tục 100 ngày",
                "threshold": 100
            }
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
                "threshold": 5
            },
            {
                "id": 21,
                "name": "Chiến binh",
                "icon": "⚔️",
                "description": "Đạt cấp độ 10",
                "threshold": 10
            },
            {
                "id": 22,
                "name": "Bậc thầy",
                "icon": "🏆",
                "description": "Đạt cấp độ 20",
                "threshold": 20
            }
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
    
    async def _check_problem_solved_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến số bài giải được
        
        Args:
            user (User): Thông tin người dùng
        """
        stats = user.stats if user.stats else {}
        problems_solved = stats.get("problems_solved", 0)
        
        # Danh sách huy hiệu problems_solved
        problem_badges = [
            {
                "id": 30,
                "name": "Coder tập sự",
                "icon": "💻",
                "description": "Giải được 10 bài tập",
                "threshold": 10
            },
            {
                "id": 31,
                "name": "Coder chuyên nghiệp",
                "icon": "👨‍💻",
                "description": "Giải được 50 bài tập",
                "threshold": 50
            },
            {
                "id": 32,
                "name": "Coder huyền thoại",
                "icon": "🧙‍♂️",
                "description": "Giải được 100 bài tập",
                "threshold": 100
            }
        ]
        
        # Kiểm tra từng huy hiệu
        for badge_data in problem_badges:
            if problems_solved >= badge_data["threshold"]:
                # Xóa trường threshold trước khi thêm huy hiệu
                badge_info = {k: v for k, v in badge_data.items() if k != "threshold"}
                await self.add_badge(user.id, badge_info)
    
    async def _check_account_age_badge(self, user: User) -> None:
        """
        Kiểm tra và cấp huy hiệu liên quan đến tuổi tài khoản
        
        Args:
            user (User): Thông tin người dùng
        """
        if not user.created_at:
            return
        
        # Tính số ngày kể từ khi tạo tài khoản
        account_age_days = (datetime.utcnow() - user.created_at).days
        
        # Danh sách huy hiệu account_age
        age_badges = [
            {
                "id": 40,
                "name": "Thành viên mới",
                "icon": "👶",
                "description": "Tài khoản đã tồn tại 30 ngày",
                "threshold": 30
            },
            {
                "id": 41,
                "name": "Thành viên trung thành",
                "icon": "👨",
                "description": "Tài khoản đã tồn tại 180 ngày",
                "threshold": 180
            },
            {
                "id": 42,
                "name": "Thành viên lâu năm",
                "icon": "👴",
                "description": "Tài khoản đã tồn tại 365 ngày",
                "threshold": 365
            }
        ]
        
        # Kiểm tra từng huy hiệu
        for badge_data in age_badges:
            if account_age_days >= badge_data["threshold"]:
                # Xóa trường threshold trước khi thêm huy hiệu
                badge_info = {k: v for k, v in badge_data.items() if k != "threshold"}
                await self.add_badge(user.id, badge_info) 