from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import random

from ..database.database import get_database
from ..models.profile import (
    ProfileResponse,
    ProfileUpdate,
    ProfileInDB,
    UserStats,
    Badge,
    Activity,
    LearningProgress,
    CourseProgress
)
from ..models.user import User

class ProfileService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["profiles"]
    
    async def get_profile(self, user_id: str) -> Optional[ProfileResponse]:
        """
        Lấy thông tin profile của một người dùng
        """
        profile_data = await self.collection.find_one({"user_id": user_id})
        if not profile_data:
            return None
        
        # Lấy thêm thông tin người dùng từ collection users
        user_data = await self.db["users"].find_one({"_id": user_id})
        if not user_data:
            return None
        
        # Kết hợp dữ liệu từ cả hai collection
        profile_data.update({
            "id": user_data["_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "created_at": user_data["created_at"]
        })
        
        return ProfileInDB(**profile_data)
    
    async def create_default_profile(self, user: User) -> ProfileResponse:
        """
        Tạo profile mặc định cho người dùng mới
        """
        # Tạo dữ liệu mặc định cho profile
        now = datetime.now()
        default_profile = {
            "user_id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "bio": "",
            "avatar_url": f"/avatars/default-{random.randint(1, 5)}.png",
            "updated_at": now,
            "stats": {
                "completed_exercises": 0,
                "completed_courses": 0,
                "total_points": 0,
                "streak_days": 0,
                "level": 1,
                "problems_solved": 0
            },
            "badges": [
                {
                    "id": 1,
                    "name": "Người mới",
                    "icon": "🔰",
                    "description": "Hoàn thành đăng ký tài khoản",
                    "unlocked": True
                }
            ],
            "activities": [],
            "learning_progress": {
                "algorithms": 0,
                "data_structures": 0,
                "dynamic_programming": 0
            },
            "courses": []
        }
        
        # Lưu vào database
        await self.collection.insert_one(default_profile)
        
        # Kết hợp với thông tin người dùng
        default_profile.update({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        })
        
        return ProfileInDB(**default_profile)
    
    async def update_profile(self, user_id: str, profile_data: ProfileUpdate) -> Optional[ProfileResponse]:
        """
        Cập nhật thông tin profile của người dùng
        """
        # Lấy profile hiện tại
        current_profile = await self.get_profile(user_id)
        if not current_profile:
            return None
        
        # Chuyển đổi Pydantic model thành dict
        update_data = profile_data.model_dump(exclude_unset=True)
        
        # Cập nhật thời gian
        update_data["updated_at"] = datetime.now()
        
        # Cập nhật trong database
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Lấy profile đã cập nhật
        return await self.get_profile(user_id)
    
    async def add_activity(self, user_id: str, activity_data: Dict[str, Any]) -> Optional[ProfileResponse]:
        """
        Thêm hoạt động mới vào profile của người dùng
        """
        # Tạo ID cho hoạt động mới
        activity_id = len(await self.get_activities(user_id)) + 1
        
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
        
        # Cập nhật trong database
        await self.collection.update_one(
            {"user_id": user_id},
            {"$push": {"activities": activity}}
        )
        
        # Cập nhật thống kê
        await self._update_stats_after_activity(user_id, activity_data)
        
        # Trả về profile đã cập nhật
        return await self.get_profile(user_id)
    
    async def get_activities(self, user_id: str, limit: int = 10) -> List[Activity]:
        """
        Lấy danh sách hoạt động của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile or not profile.activities:
            return []
        
        # Sắp xếp theo thời gian giảm dần và giới hạn số lượng
        activities = sorted(
            profile.activities,
            key=lambda x: datetime.strptime(x.date, "%d/%m/%Y"),
            reverse=True
        )
        
        return activities[:limit]
    
    async def add_badge(self, user_id: str, badge_data: Dict[str, Any]) -> Optional[ProfileResponse]:
        """
        Thêm huy hiệu mới vào profile của người dùng
        """
        # Kiểm tra huy hiệu đã tồn tại chưa
        existing_badges = await self._get_badges(user_id)
        
        badge_id = badge_data.get("id")
        if any(badge.id == badge_id for badge in existing_badges):
            # Cập nhật trạng thái huy hiệu đã có
            await self.collection.update_one(
                {"user_id": user_id, "badges.id": badge_id},
                {"$set": {"badges.$.unlocked": badge_data.get("unlocked", True)}}
            )
        else:
            # Thêm huy hiệu mới
            badge = {
                "id": badge_id,
                "name": badge_data.get("name"),
                "icon": badge_data.get("icon"),
                "description": badge_data.get("description"),
                "unlocked": badge_data.get("unlocked", True)
            }
            
            await self.collection.update_one(
                {"user_id": user_id},
                {"$push": {"badges": badge}}
            )
        
        # Trả về profile đã cập nhật
        return await self.get_profile(user_id)
    
    async def _get_badges(self, user_id: str) -> List[Badge]:
        """
        Lấy danh sách huy hiệu của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile or not profile.badges:
            return []
        
        return profile.badges
    
    async def update_learning_progress(self, user_id: str, progress_data: Dict[str, int]) -> Optional[ProfileResponse]:
        """
        Cập nhật tiến độ học tập của người dùng
        """
        # Lấy tiến độ hiện tại
        profile = await self.get_profile(user_id)
        if not profile:
            return None
        
        # Tạo dữ liệu cập nhật
        update_data = {}
        for key, value in progress_data.items():
            update_data[f"learning_progress.{key}"] = value
        
        # Cập nhật trong database
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Trả về profile đã cập nhật
        return await self.get_profile(user_id)
    
    async def update_course_progress(self, user_id: str, course_id: str, progress: int) -> Optional[ProfileResponse]:
        """
        Cập nhật tiến độ khóa học
        """
        # Kiểm tra khóa học đã tồn tại chưa
        profile = await self.get_profile(user_id)
        if not profile:
            return None
        
        existing_course = next((c for c in profile.courses if c.id == course_id), None)
        
        if existing_course:
            # Cập nhật tiến độ khóa học đã có
            await self.collection.update_one(
                {"user_id": user_id, "courses.id": course_id},
                {"$set": {"courses.$.progress": progress}}
            )
        else:
            # Lấy thông tin khóa học từ database
            course = await self.db["courses"].find_one({"_id": course_id})
            if not course:
                return None
            
            # Thêm khóa học mới
            new_course = {
                "id": course_id,
                "name": course.get("name"),
                "progress": progress,
                "color_from": course.get("color_from", "blue-500"),
                "color_to": course.get("color_to", "blue-700"),
                "image_url": course.get("image_url")
            }
            
            await self.collection.update_one(
                {"user_id": user_id},
                {"$push": {"courses": new_course}}
            )
        
        # Trả về profile đã cập nhật
        return await self.get_profile(user_id)
    
    async def _update_stats_after_activity(self, user_id: str, activity_data: Dict[str, Any]) -> None:
        """
        Cập nhật thống kê người dùng sau khi có hoạt động mới
        
        Args:
            user_id (str): ID của người dùng
            activity_data (Dict[str, Any]): Dữ liệu hoạt động
        """
        activity_type = activity_data.get("type")
        
        update_data = {}
        
        if activity_type == "exercise":
            # Tăng số bài tập đã hoàn thành
            update_data["stats.completed_exercises"] = 1
            # Tăng số bài thuật toán đã giải
            update_data["stats.problems_solved"] = 1
            # Tăng điểm tổng
            update_data["stats.total_points"] = int(activity_data.get("score", "0").split("/")[0])
            
        elif activity_type == "course" and activity_data.get("progress") == "100%":
            # Tăng số khóa học đã hoàn thành
            update_data["stats.completed_courses"] = 1
            # Tăng điểm tổng
            update_data["stats.total_points"] = 100
        
        if update_data:
            # Cập nhật trong database
            await self.collection.update_one(
                {"user_id": user_id},
                {"$inc": update_data}
            )
            
            # Kiểm tra và cập nhật level
            await self._update_level(user_id)
            
            # Kiểm tra và cập nhật huy hiệu dựa trên số bài tập đã giải
            if "stats.problems_solved" in update_data:
                await self._check_problem_solved_badge(user_id)
    
    async def _update_level(self, user_id: str) -> None:
        """
        Cập nhật level người dùng dựa trên tổng điểm
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        total_points = profile.stats.total_points
        
        # Công thức tính level: Mỗi 100 điểm tăng 1 level
        new_level = max(1, total_points // 100 + 1)
        
        if new_level > profile.stats.level:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"stats.level": new_level}}
            )
    
    async def update_streak(self, user_id: str) -> None:
        """
        Cập nhật chuỗi hoạt động liên tiếp của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        # Lấy thời gian hoạt động gần nhất
        last_activity = await self.db["user_activity_logs"].find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        if not last_activity:
            # Đây là lần đầu hoạt động
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"stats.streak_days": 1}}
            )
            return
        
        last_activity_date = last_activity["timestamp"].date()
        today = datetime.utcnow().date()
        
        if today == last_activity_date:
            # Đã có hoạt động hôm nay, không làm gì
            return
        elif today == last_activity_date + timedelta(days=1):
            # Hoạt động liên tiếp, tăng streak
            await self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"stats.streak_days": 1}}
            )
        else:
            # Đã bỏ lỡ ít nhất một ngày, reset streak
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"stats.streak_days": 1}}
            )
        
        # Kiểm tra và trao huy hiệu
        await self._check_streak_badge(user_id)
    
    async def _check_streak_badge(self, user_id: str) -> None:
        """
        Kiểm tra và trao huy hiệu dựa trên chuỗi ngày giải bài liên tiếp
        
        Args:
            user_id (str): ID của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        current_streak = profile.stats.streak_days
        
        # Danh sách huy hiệu dựa trên chuỗi ngày giải bài liên tiếp
        streak_badges = [
            {
                "id": 401,
                "name": "Khởi đầu chăm chỉ",
                "icon": "🔥",
                "description": "Giải bài 3 ngày liên tiếp",
                "unlocked": True,
                "threshold": 3
            },
            {
                "id": 402,
                "name": "Tinh thần kiên trì",
                "icon": "🔥🔥",
                "description": "Giải bài 7 ngày liên tiếp",
                "unlocked": True,
                "threshold": 7
            },
            {
                "id": 403,
                "name": "Nghiện thuật toán",
                "icon": "🔥🔥🔥",
                "description": "Giải bài 14 ngày liên tiếp",
                "unlocked": True,
                "threshold": 14
            },
            {
                "id": 404,
                "name": "Chuyên gia bền bỉ",
                "icon": "⚡🔥⚡",
                "description": "Giải bài 30 ngày liên tiếp",
                "unlocked": True,
                "threshold": 30
            }
        ]
        
        # Lấy danh sách ID của các huy hiệu hiện có
        existing_badge_ids = [badge.id for badge in profile.badges] if profile.badges else []
        
        # Kiểm tra và trao huy hiệu mới
        for badge in streak_badges:
            if current_streak >= badge["threshold"] and badge["id"] not in existing_badge_ids:
                # Loại bỏ field threshold trước khi thêm vào database
                badge_data = {k: v for k, v in badge.items() if k != "threshold"}
                
                # Thêm huy hiệu mới
                await self.add_badge(user_id, badge_data)
                
                # Thêm hoạt động mới về việc đạt được huy hiệu
                activity_data = {
                    "type": "badge",
                    "name": f"Đạt được huy hiệu {badge['name']}"
                }
                
                await self.add_activity(user_id, activity_data)
    
    async def _check_level_badge(self, user_id: str) -> None:
        """
        Kiểm tra và trao huy hiệu dựa trên cấp độ người dùng
        
        Args:
            user_id (str): ID của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        current_level = profile.stats.level
        
        # Danh sách huy hiệu dựa trên cấp độ
        level_badges = [
            {
                "id": 201,
                "name": "Tân binh",
                "icon": "🥉",
                "description": "Đạt cấp độ 5",
                "unlocked": True,
                "threshold": 5
            },
            {
                "id": 202,
                "name": "Nhà giải thuật trung cấp",
                "icon": "🥈",
                "description": "Đạt cấp độ 10",
                "unlocked": True,
                "threshold": 10
            },
            {
                "id": 203,
                "name": "Chuyên gia giải thuật",
                "icon": "🥇",
                "description": "Đạt cấp độ 20",
                "unlocked": True,
                "threshold": 20
            },
            {
                "id": 204,
                "name": "Bậc thầy thuật toán",
                "icon": "👑",
                "description": "Đạt cấp độ 30",
                "unlocked": True,
                "threshold": 30
            }
        ]
        
        # Lấy danh sách ID của các huy hiệu hiện có
        existing_badge_ids = [badge.id for badge in profile.badges] if profile.badges else []
        
        # Kiểm tra và trao huy hiệu mới
        for badge in level_badges:
            if current_level >= badge["threshold"] and badge["id"] not in existing_badge_ids:
                # Loại bỏ field threshold trước khi thêm vào database
                badge_data = {k: v for k, v in badge.items() if k != "threshold"}
                
                # Thêm huy hiệu mới
                await self.add_badge(user_id, badge_data)
                
                # Thêm hoạt động mới về việc đạt được huy hiệu
                activity_data = {
                    "type": "badge",
                    "name": f"Đạt được huy hiệu {badge['name']}"
                }
                
                await self.add_activity(user_id, activity_data)
    
    async def _check_problem_solved_badge(self, user_id: str) -> None:
        """
        Kiểm tra và trao huy hiệu dựa trên số bài tập đã giải
        
        Args:
            user_id (str): ID của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        problems_solved = profile.stats.problems_solved
        
        # Danh sách huy hiệu dựa trên số bài tập đã giải
        problem_badges = [
            {
                "id": 301,
                "name": "Giải quyết vấn đề cơ bản",
                "icon": "🔰",
                "description": "Giải được 10 bài tập",
                "unlocked": True,
                "threshold": 10
            },
            {
                "id": 302,
                "name": "Người giải quyết vấn đề",
                "icon": "⭐",
                "description": "Giải được 50 bài tập",
                "unlocked": True,
                "threshold": 50
            },
            {
                "id": 303,
                "name": "Cao thủ giải bài",
                "icon": "🌟",
                "description": "Giải được 100 bài tập",
                "unlocked": True,
                "threshold": 100
            },
            {
                "id": 304,
                "name": "Quái kiệt thuật toán",
                "icon": "💫",
                "description": "Giải được 200 bài tập",
                "unlocked": True,
                "threshold": 200
            }
        ]
        
        # Lấy danh sách ID của các huy hiệu hiện có
        existing_badge_ids = [badge.id for badge in profile.badges] if profile.badges else []
        
        # Kiểm tra và trao huy hiệu mới
        for badge in problem_badges:
            if problems_solved >= badge["threshold"] and badge["id"] not in existing_badge_ids:
                # Loại bỏ field threshold trước khi thêm vào database
                badge_data = {k: v for k, v in badge.items() if k != "threshold"}
                
                # Thêm huy hiệu mới
                await self.add_badge(user_id, badge_data)
                
                # Thêm hoạt động mới về việc đạt được huy hiệu
                activity_data = {
                    "type": "badge",
                    "name": f"Đạt được huy hiệu {badge['name']}"
                }
                
                await self.add_activity(user_id, activity_data)
    
    async def _check_account_age_badge(self, user_id: str) -> None:
        """
        Kiểm tra và trao huy hiệu dựa trên thời gian hoạt động của tài khoản
        
        Args:
            user_id (str): ID của người dùng
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return
        
        # Tính số ngày tài khoản đã hoạt động
        created_at = profile.created_at
        current_time = datetime.datetime.now(datetime.timezone.utc)
        account_age_days = (current_time - created_at).days
        
        # Danh sách huy hiệu dựa trên thời gian hoạt động
        account_age_badges = [
            {
                "id": 501,
                "name": "Thành viên mới",
                "icon": "🌱",
                "description": "Đã tham gia được 7 ngày",
                "unlocked": True,
                "threshold": 7
            },
            {
                "id": 502,
                "name": "Thành viên tích cực",
                "icon": "🌿",
                "description": "Đã tham gia được 30 ngày",
                "unlocked": True,
                "threshold": 30
            },
            {
                "id": 503,
                "name": "Thành viên lâu năm",
                "icon": "🌲",
                "description": "Đã tham gia được 90 ngày",
                "unlocked": True,
                "threshold": 90
            },
            {
                "id": 504,
                "name": "Cựu binh",
                "icon": "🏆🌳",
                "description": "Đã tham gia được 365 ngày",
                "unlocked": True,
                "threshold": 365
            }
        ]
        
        # Lấy danh sách ID của các huy hiệu hiện có
        existing_badge_ids = [badge.id for badge in profile.badges] if profile.badges else []
        
        # Kiểm tra và trao huy hiệu mới
        for badge in account_age_badges:
            if account_age_days >= badge["threshold"] and badge["id"] not in existing_badge_ids:
                # Loại bỏ field threshold trước khi thêm vào database
                badge_data = {k: v for k, v in badge.items() if k != "threshold"}
                
                # Thêm huy hiệu mới
                await self.add_badge(user_id, badge_data)
                
                # Thêm hoạt động mới về việc đạt được huy hiệu
                activity_data = {
                    "type": "badge",
                    "name": f"Đạt được huy hiệu {badge['name']}"
                }
                
                await self.add_activity(user_id, activity_data)
    
    async def update_badges(self, user_id: str) -> None:
        """
        Cập nhật huy hiệu của người dùng
        
        Args:
            user_id (str): ID của người dùng
        """
        # Kiểm tra huy hiệu streak
        await self._check_streak_badge(user_id)
        
        # Kiểm tra huy hiệu dựa trên thời gian hoạt động
        await self._check_account_age_badge(user_id)
        
        # Kiểm tra huy hiệu dựa trên số bài tập đã giải
        await self._check_problem_solved_badge(user_id)
        
        # Kiểm tra huy hiệu dựa trên cấp độ
        await self._check_level_badge(user_id)
        
        # TODO: Thêm các loại huy hiệu khác trong tương lai 