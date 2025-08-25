from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models.topic_model import Topic
from app.schemas.course_draft_schema import TopicOrderRequest
from app.schemas.topic_schema import (
    TopicCreate,
    TopicWithLesson,
    TopicUpdate,
    TopicCourseAssignment,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_draft_service import (
    reorder_topic_course_draft,
)
from app.utils.utils import get_current_user

router = APIRouter(
    prefix="/admin/topics",
    tags=["admin-topics"],
    responses={404: {"description": "Không tìm thấy chủ đề"}},
)


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.post(
    "",
    response_model=TopicWithLesson,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo chủ đề mới (Admin)",
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def create_topic(
        topic_data: TopicCreate,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo một chủ đề mới cho một khóa học (chỉ admin)
    """
    try:
        new_topic = Topic(**topic_data.model_dump())
        db.add(new_topic)
        await db.commit()
        await db.refresh(new_topic)
        return new_topic
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo chủ đề: {str(e)}",
        )


@router.get(
    "",
    response_model=List[TopicWithLesson],
    summary="Lấy danh sách chủ đề (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
    },
)
async def get_topics_admin(
        course_id: int | None = None,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    query = select(Topic).options(selectinload(Topic.lessons))
    if course_id is not None:
        query = query.filter(Topic.course_id == course_id)
    result = await db.execute(query)
    topics = result.scalars().all()
    return topics


@router.get(
    "/{topic_id}",
    response_model=TopicWithLesson,
    summary="Lấy chi tiết chủ đề (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy chủ đề"},
    },
)
async def get_topic_by_id_admin(
        topic_id: int,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy thông tin chi tiết của một chủ đề (chỉ admin)
    """
    result = await db.execute(select(Topic).filter(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {topic_id}",
        )
    return topic


@router.put(
    "/{topic_id}",
    response_model=TopicWithLesson,
    summary="Cập nhật chủ đề (Admin)",
    responses={
        200: {"description": "OK"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy chủ đề"},
        500: {"description": "Internal server error"},
    },
)
async def update_topic(
        topic_id: int,
        topic_data: TopicUpdate,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Cập nhật thông tin chủ đề (chỉ admin)
    """
    result = await db.execute(select(Topic).filter(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {topic_id}",
        )

    try:
        # Cập nhật các field được gửi lên
        update_data = topic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)

        # Lưu thay đổi
        await db.commit()
        await db.refresh(topic)

        return topic
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật chủ đề: {str(e)}",
        )


@router.patch(
    "/{topic_id}/assign-course",
    response_model=TopicWithLesson,
    summary="Assign/Unassign khóa học cho chủ đề (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy chủ đề"},
        500: {"description": "Internal server error"},
    },
)
async def assign_topic_to_course(
        topic_id: int,
        assignment_data: TopicCourseAssignment,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    result = await db.execute(select(Topic).filter(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {topic_id}",
        )

    try:
        # Cập nhật course_id
        topic.course_id = assignment_data.course_id
        await db.commit()
        await db.refresh(topic)
        return topic
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi assign chủ đề: {str(e)}",
        )


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa chủ đề (Admin)",
    responses={
        204: {"description": "Xóa thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy chủ đề"},
        500: {"description": "Internal server error"},
    },
)
async def delete_topic(
        topic_id: int,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa chủ đề (chỉ admin)
    """
    result = await db.execute(select(Topic).filter(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {topic_id}",
        )

    try:
        # Xóa chủ đề
        await db.delete(topic)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa chủ đề: {str(e)}",
        )


@router.put("/draft/{course_id}")
async def reorder(
        topics: TopicOrderRequest,
        course_id: int,
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    return reorder_topic_course_draft(topics, course_id)
