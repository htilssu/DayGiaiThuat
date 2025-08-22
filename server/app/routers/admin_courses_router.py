import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_async_db
from app.models.course_model import Course
from app.schemas.course_draft_schema import CourseDraftSchema
from app.schemas.course_review_schema import ApproveDraftRequest
from app.schemas.course_schema import (
    BulkDeleteCoursesRequest,
    BulkDeleteCoursesResponse,
    CourseCompositionRequestSchema,
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_draft_service import (
    get_course_draft_by_course_id,
    approve_course_draft_handler,
)
from app.services.course_generate_service import (
    CourseGenerateService,
    get_course_generate_service,
)
from app.services.course_service import CourseService, get_course_service
from app.services.lesson_generate_service import LessonGenerateService
from app.services.test_generation_service import (
    TestGenerationService,
    get_test_generation_service,
)
from app.services.topic_draft_service import approve_topic_draft_handler
from app.utils.utils import get_current_user

router = APIRouter(
    prefix="/admin/courses",
    tags=["Khóa học - Admin"],
    responses={404: {"description": "Không tìm thấy khóa học"}},
)


class ThumbnailUpdateRequest(BaseModel):
    thumbnail_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "thumbnail_url": "https://example.com/images/course-thumbnail.jpg"
            }
        }


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.patch(
    "/{course_id}/thumbnail",
    response_model=CourseResponse,
    summary="Cập nhật ảnh thumbnail khóa học (Admin)",
    responses={
        200: {"description": "Cập nhật thành công"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def update_course_thumbnail(
        course_id: int,
        thumbnail_data: ThumbnailUpdateRequest,
        course_service: CourseService = Depends(get_course_service),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    try:
        updated_course = await course_service.update_course_thumbnail(
            course_id, thumbnail_data.thumbnail_url
        )
        return updated_course
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật ảnh thumbnail: {str(e)}",
        )


@router.get(
    "/{course_id}/review",
    response_model=CourseResponse,
    summary="Lấy thông tin review khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def get_course_review(
        course_id: int,
        admin_user: UserExcludeSecret = Depends(get_admin_user),
        course_service: CourseService = Depends(get_course_service),
):
    course = await course_service.get_course(course_id)
    return CourseResponse.model_validate(course)


@router.post(
    "/{course_id}/review/approve",
    summary="Approve draft và lưu vào database (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học hoặc draft"},
    },
)
async def approve_course_draft(
        course_id: int,
        approve_request: ApproveDraftRequest,
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    await approve_course_draft_handler(course_id, approve_request)
    return get_course_draft_by_course_id(course_id)


@router.post("/{course_id}/topic/reject", )
async def reject_topic_draft(
        course_id: int,
        approve_request: ApproveDraftRequest,
        admin_user: UserExcludeSecret = Depends(get_admin_user)
):
    approve_request.approved = False
    await approve_course_draft_handler(course_id, approve_request)
    return get_course_draft_by_course_id(course_id)


@router.post(
    "/{course_id}/topic/approve",
    summary="Approve topic draft và lưu vào database (Admin)",
)
async def approve_topic_draft(
        course_id: int, admin_user: UserExcludeSecret = Depends(get_admin_user)
):
    topic_list = await approve_topic_draft_handler(course_id)
    lesson_generate_service = LessonGenerateService()
    asyncio.create_task(lesson_generate_service.generate_all_by_topic(topic_list))
    return {
        "message": "Đã phê duyệt bản nháp topic thành công",
    }


@router.delete(
    "/bulk",
    response_model=BulkDeleteCoursesResponse,
    summary="Xóa nhiều khóa học cùng lúc (Admin)",
    responses={
        200: {"description": "Xóa thành công"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def bulk_delete_courses(
        request: BulkDeleteCoursesRequest,
        course_service: CourseService = Depends(get_course_service),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    try:
        if not request.course_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Danh sách course_ids không được rỗng",
            )

        result = await course_service.bulk_delete_courses(request.course_ids)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi không xác định khi xóa khóa học: {str(e)}",
        )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa khóa học (Admin)",
    responses={
        200: {"description": "Xóa thành công"},
        400: {"description": "Khóa học đang được sử dụng"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def delete_course(
        course_id: int,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
        force: Annotated[
            int, Query(ge=0, le=1, description="Force delete without checking enrollments")
        ] = 0,
):
    from app.models.lesson_model import Lesson, LessonSection
    from app.models.topic_model import Topic
    from app.models.user_course_model import UserCourse

    course = await db.execute(select(Course).where(Course.id == course_id))
    course = course.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    enrollment_count = (
        await db.execute(select(func.count()).where(UserCourse.course_id == course_id))
    ).scalar()
    if force == 0:
        enrollment_count = (
            await db.execute(
                select(func.count()).where(UserCourse.course_id == course_id)
            )
        ).scalar()

    else:
        enrollment_count = 0

    if enrollment_count is not None and enrollment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Khóa học '{course.title}' đang được sử dụng bởi {enrollment_count} người dùng. Không thể xóa.",
                "type": "course_in_use",
                "id": course_id,
            },
        )

    try:
        topics_count = await db.execute(
            select(func.count()).where(Topic.course_id == course_id)
        )
        lessons_count = await db.execute(
            select(func.count())
            .select_from(Lesson)
            .join(Topic, Lesson.topic_id == Topic.id)
            .filter(Topic.course_id == course_id)
        )
        sections_count = await db.execute(
            select(func.count())
            .select_from(LessonSection)
            .join(Lesson, LessonSection.lesson_id == Lesson.id)
            .join(Topic, Lesson.topic_id == Topic.id)
            .filter(Topic.course_id == course_id)
        )
        topics_count = topics_count.scalar()
        lessons_count = lessons_count.scalar()
        sections_count = sections_count.scalar()
        topics_count = topics_count or 0
        lessons_count = lessons_count or 0
        sections_count = sections_count or 0
        await db.delete(course)
        await db.commit()

        return {
            "message": f"Đã xóa thành công khóa học '{course.title}' và tất cả dữ liệu liên quan",
            "deleted_items": {
                "courses": 1,
                "topics": topics_count,
                "lessons": lessons_count,
                "lesson_sections": sections_count,
            },
        }
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}",
        )
    finally:
        await db.close()


@router.post(
    "/{course_id}/test",
    summary="Tạo bài kiểm tra đầu vào cho khóa học - Async (Admin)",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def create_test(
        course_id: int,
        test_generation_service: TestGenerationService = Depends(
            get_test_generation_service
        ),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    await test_generation_service.generate_input_test_async(course_id)
    return {"message": "Đã bắt đầu tạo test trong background", "course_id": course_id}


@router.get(
    "",
    summary="Lấy tất cả khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
    },
)
async def get_all_courses_admin(
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.topics))
        .order_by(Course.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Lấy chi tiết khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def get_course_by_id_admin(
        course_id: int,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    from app.schemas.course_schema import CourseListItem

    return CourseListItem.model_validate(course)


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo khóa học mới (Admin)",
    responses={
        201: {"description": "Created"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def create_course(
        course_data: CourseCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_async_db),
        course_generate_service: CourseGenerateService = Depends(
            get_course_generate_service
        ),
        course_service: CourseService = Depends(get_course_service),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    try:
        new_course = await course_service.create_course(course_data)

        composition_request = CourseCompositionRequestSchema(
            course_id=new_course.id,
            course_title=new_course.title,
            course_description=new_course.description,
            course_level=new_course.level,
            session_id=str(uuid.uuid4()),
        )

        asyncio.create_task(
            course_generate_service.background_create(composition_request)
        )

        return new_course
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo khóa học: {str(e)}",
        )


@router.put(
    "/{course_id}",
    response_model=CourseUpdate,
    summary="Cập nhật khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
        500: {"description": "Internal server error"},
    },
)
async def update_course(
        course_id: int,
        course_data: CourseUpdate,
        db: AsyncSession = Depends(get_async_db),
        admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        update_data = course_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await db.commit()
        await db.refresh(course)

        result = await db.execute(select(Course).filter(Course.id == course_id))
        updated_course = result.scalar_one()

        return CourseUpdate.from_model(model=updated_course)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
        )
