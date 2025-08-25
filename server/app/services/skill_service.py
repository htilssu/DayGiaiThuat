"""
Service để xử lý logic nghiệp vụ cho Skill
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.skill_model import Skill
from app.schemas.skill_schema import SkillCreate, SkillUpdate


class SkillService:
    """Service để quản lý skill"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_skill(self, skill_data: SkillCreate) -> Skill:
        """
        Tạo mới một skill

        Args:
            skill_data: Dữ liệu để tạo skill

        Returns:
            Skill: Skill đã được tạo
        """
        skill = Skill(**skill_data.dict())
        self.db_session.add(skill)
        await self.db_session.commit()
        await self.db_session.refresh(skill)
        return skill

    async def get_skill_by_id(self, skill_id: int) -> Optional[Skill]:
        """
        Lấy skill theo ID

        Args:
            skill_id: ID của skill

        Returns:
            Optional[Skill]: Skill nếu tìm thấy, None nếu không
        """
        result = await self.db_session.execute(
            select(Skill).options(selectinload(Skill.topic)).where(Skill.id == skill_id)
        )
        return result.scalar_one_or_none()

    async def get_skills_by_topic_id(self, topic_id: int) -> List[Skill]:
        """
        Lấy tất cả skills của một topic

        Args:
            topic_id: ID của topic

        Returns:
            List[Skill]: Danh sách skills
        """
        result = await self.db_session.execute(
            select(Skill).where(Skill.topic_id == topic_id).order_by(Skill.id)
        )
        return list(result.scalars().all())

    async def update_skill(
        self, skill_id: int, skill_data: SkillUpdate
    ) -> Optional[Skill]:
        """
        Cập nhật thông tin skill

        Args:
            skill_id: ID của skill cần cập nhật
            skill_data: Dữ liệu cập nhật

        Returns:
            Optional[Skill]: Skill đã cập nhật hoặc None nếu không tìm thấy
        """
        # Lọc bỏ các giá trị None
        update_data = {k: v for k, v in skill_data.dict().items() if v is not None}

        if not update_data:
            return await self.get_skill_by_id(skill_id)

        await self.db_session.execute(
            update(Skill).where(Skill.id == skill_id).values(**update_data)
        )
        await self.db_session.commit()

        return await self.get_skill_by_id(skill_id)

    async def delete_skill(self, skill_id: int) -> bool:
        """
        Xóa skill

        Args:
            skill_id: ID của skill cần xóa

        Returns:
            bool: True nếu xóa thành công, False nếu không tìm thấy
        """
        result = await self.db_session.execute(
            delete(Skill).where(Skill.id == skill_id)
        )
        await self.db_session.commit()

        return result.rowcount > 0

    async def create_multiple_skills(
        self, skills_data: List[SkillCreate]
    ) -> List[Skill]:
        """
        Tạo nhiều skills cùng lúc

        Args:
            skills_data: Danh sách dữ liệu skill

        Returns:
            List[Skill]: Danh sách skills đã tạo
        """
        skills = [Skill(**skill_data.dict()) for skill_data in skills_data]
        self.db_session.add_all(skills)
        await self.db_session.commit()

        # Refresh tất cả skills
        for skill in skills:
            await self.db_session.refresh(skill)

        return skills
