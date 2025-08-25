"""
API router cho quản lý skills
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_db
from app.services.skill_service import SkillService
from app.schemas.skill_schema import SkillCreate, SkillUpdate, SkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate, db: AsyncSession = Depends(get_async_db)
):
    """Tạo mới một skill"""
    skill_service = SkillService(db)
    skill = await skill_service.create_skill(skill_data)
    return skill


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: AsyncSession = Depends(get_async_db)):
    """Lấy thông tin skill theo ID"""
    skill_service = SkillService(db)
    skill = await skill_service.get_skill_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill không tìm thấy"
        )

    return skill


@router.get("/topic/{topic_id}", response_model=List[SkillResponse])
async def get_skills_by_topic(topic_id: int, db: AsyncSession = Depends(get_async_db)):
    """Lấy tất cả skills của một topic"""
    skill_service = SkillService(db)
    skills = await skill_service.get_skills_by_topic_id(topic_id)
    return skills


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int, skill_data: SkillUpdate, db: AsyncSession = Depends(get_async_db)
):
    """Cập nhật thông tin skill"""
    skill_service = SkillService(db)
    skill = await skill_service.update_skill(skill_id, skill_data)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill không tìm thấy"
        )

    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: int, db: AsyncSession = Depends(get_async_db)):
    """Xóa skill"""
    skill_service = SkillService(db)
    success = await skill_service.delete_skill(skill_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill không tìm thấy"
        )


@router.post(
    "/bulk", response_model=List[SkillResponse], status_code=status.HTTP_201_CREATED
)
async def create_multiple_skills(
    skills_data: List[SkillCreate], db: AsyncSession = Depends(get_async_db)
):
    """Tạo nhiều skills cùng lúc"""
    skill_service = SkillService(db)
    skills = await skill_service.create_multiple_skills(skills_data)
    return skills
