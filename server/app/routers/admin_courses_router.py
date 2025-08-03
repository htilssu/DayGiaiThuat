from app.core.agents.course_composition_agent import CourseCompositionAgent
from app.database.database import get_async_db, get_independent_db_session
from app.models.course_model import Course
from app.models.topic_model import Topic
from app.models.course_draft_model import CourseDraft, CourseReviewChat
from app.schemas.course_schema import (
    BulkDeleteCoursesRequest,
    BulkDeleteCoursesResponse,
    CourseCompositionRequestSchema,
    CourseCreate,
    CourseOnlyResponse,
    CourseResponse,
    CourseUpdate,
)
from app.schemas.course_review_schema import (
    CourseReviewResponse,
    SendChatMessageRequest,
    ApproveDraftRequest,
    CourseReviewChatMessage,
    CourseDraftResponse,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_service import CourseService, get_course_service
from app.services.test_generation_service import (
    TestGenerationService,
    get_test_generation_service,
)
from app.utils.utils import get_current_user
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

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
    """Kiểm tra quyền admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


async def run_course_composition_background(
    request: CourseCompositionRequestSchema, db: AsyncSession
):
    """
    Hàm chạy trong background để tạo nội dung khóa học.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        agent = CourseCompositionAgent(db)
        agent_response, session_id = await agent.act(request)

        # Lưu kết quả vào draft
        import json

        # Kiểm tra xem có draft nào cho course này chưa
        from sqlalchemy import select

        existing_draft_result = await db.execute(
            select(CourseDraft).filter(CourseDraft.course_id == request.course_id)
        )
        existing_draft = existing_draft_result.scalar_one_or_none()

        topics_json = json.dumps(
            agent_response.model_dump(), ensure_ascii=False, indent=2
        )

        if existing_draft:
            # Cập nhật draft hiện có
            existing_draft.agent_content = topics_json
            existing_draft.session_id = session_id
            existing_draft.status = "pending"
            from datetime import datetime

            existing_draft.updated_at = datetime.utcnow()
        else:
            # Tạo draft mới
            new_draft = CourseDraft(
                course_id=request.course_id,
                agent_content=topics_json,
                session_id=session_id,
                status="pending",
            )
            db.add(new_draft)

        await db.commit()
        logger.info(
            f"✅ Course composition completed and saved to draft for course: {request.course_id} with session: {session_id}"
        )

    except Exception as e:
        logger.error(f"❌ Error in course composition: {str(e)}")
        await db.rollback()
        raise e


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
    course_service: CourseService = Depends(get_course_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo một khóa học mới (chỉ admin)

    Raises:
        HTTPException: Nếu có lỗi khi tạo khóa học
        :param course_data:
        :param admin_user:
        :param course_service:
        :param db:
        :param background_tasks:
    """
    try:
        new_course = await course_service.create_course(course_data)

        # Run course composition in the background
        composition_request = CourseCompositionRequestSchema(
            course_id=new_course.id,
            course_title=new_course.title,
            course_description=new_course.description,
            course_level=new_course.level,
            session_id=None,  # Sẽ được tạo tự động trong agent
        )
        background_tasks.add_task(
            run_course_composition_background, composition_request, db
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
    response_model=CourseResponse,
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
    """
    Cập nhật thông tin khóa học (chỉ admin)

    Args:
        course_id: ID của khóa học cần cập nhật
        course_data: Dữ liệu cập nhật
        db: Session database
        admin_user: Thông tin admin đã xác thực

    Returns:
        CourseResponse: Thông tin khóa học sau khi cập nhật

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi cập nhật
    """
    # Tìm khóa học cần cập nhật
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        # Cập nhật các field được gửi lên
        update_data = course_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        # Lưu thay đổi
        await db.commit()
        await db.refresh(course)

        # Tải lại course với topics để tránh lỗi lazy loading
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.lessons))
            .filter(Course.id == course_id)
        )
        updated_course = result.scalar_one()

        return CourseOnlyResponse.model_validate(updated_course)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
        )


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
    """
    Xóa nhiều khóa học cùng lúc (chỉ admin)

    Args:
        request: Danh sách ID các khóa học cần xóa
        course_service: Service xử lý khóa học
        admin_user: Thông tin admin đã xác thực

    Returns:
        BulkDeleteCoursesResponse: Thông tin về quá trình xóa

    Raises:
        HTTPException: Nếu có lỗi trong quá trình xóa
    """
    try:
        # Validate danh sách course_ids
        if not request.course_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Danh sách course_ids không được rỗng",
            )

        # Thực hiện bulk delete
        result = await course_service.bulk_delete_courses(request.course_ids)

        return result

    except HTTPException:
        # Re-raise HTTPException từ validation
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
    force: int = Query(
        default=0, ge=0, le=1, description="Force delete without checking enrollments"
    ),
    db: AsyncSession = Depends(get_async_db),
    course_service: CourseService = Depends(get_course_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa khóa học và tất cả dữ liệu liên quan (chỉ admin)

    Args:
        course_id: ID của khóa học cần xóa
        db: Session database
        admin_user: Thông tin admin đã xác thực

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi xóa

    Returns:
        dict: Thông tin về quá trình xóa bao gồm số lượng items đã xóa
        :param course_id:
        :param admin_user:
        :param course_service:
        :param db:
        :param force:
    """
    from app.models.lesson_model import Lesson, LessonSection
    from app.models.topic_model import Topic
    from app.models.user_course_model import UserCourse

    # Tìm khóa học cần xóa
    course = await db.execute(select(Course).where(Course.id == course_id))
    course = course.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    # Kiểm tra xem khóa học có đang được sử dụng không
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
        # Đếm số lượng items sẽ bị xóa để logging
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
        # Xóa khóa học (cascade sẽ tự động xóa topics, lessons, sections)
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
    """
    Tạo bài kiểm tra đầu vào cho khóa học - Background (chỉ admin)
    """
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
    """
    Lấy tất cả khóa học bao gồm cả chưa được published (chỉ admin)
    """
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
    """
    Lấy thông tin chi tiết của một khóa học (chỉ admin, bao gồm cả chưa published)
    """
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    from app.schemas.course_schema import CourseListItem

    return CourseListItem.model_validate(course)


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
    """
    Cập nhật ảnh thumbnail cho khóa học (chỉ admin)

    Args:
        course_id (int): ID của khóa học
        thumbnail_data (ThumbnailUpdateRequest): Dữ liệu ảnh thumbnail mới
        course_service (CourseService): Service xử lý khóa học
        admin_user (UserExcludeSecret): Thông tin admin đã xác thực

    Returns:
        CourseResponse: Thông tin khóa học sau khi cập nhật

    Raises:
        HTTPException: Nếu không tìm thấy khóa học hoặc có lỗi khi cập nhật
    """
    try:
        # Cập nhật thumbnail thông qua service
        updated_course = await course_service.update_course_thumbnail(
            course_id, thumbnail_data.thumbnail_url
        )
        return updated_course
    except HTTPException:
        # Re-raise HTTPException từ service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật ảnh thumbnail: {str(e)}",
        )


# API endpoints mới cho workflow review
@router.get(
    "/{course_id}/review",
    response_model=CourseReviewResponse,
    summary="Lấy thông tin review khóa học (Admin)",
    responses={
        200: {"description": "OK"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def get_course_review(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy thông tin review khóa học bao gồm draft content và chat history
    """
    # Tìm course
    course_result = await db.execute(select(Course).filter(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    # Tìm draft gần nhất
    draft_result = await db.execute(
        select(CourseDraft)
        .filter(CourseDraft.course_id == course_id)
        .order_by(CourseDraft.created_at.desc())
        .limit(1)
    )
    draft = draft_result.scalar_one_or_none()

    # Lấy chat history
    chat_result = await db.execute(
        select(CourseReviewChat)
        .filter(CourseReviewChat.course_id == course_id)
        .order_by(CourseReviewChat.created_at.asc())
    )
    chat_messages = chat_result.scalars().all()

    return CourseReviewResponse(
        course_id=course.id,
        course_title=course.title,
        course_description=course.description,
        draft=CourseDraftResponse.model_validate(draft) if draft else None,
        chat_messages=[
            CourseReviewChatMessage.model_validate(msg) for msg in chat_messages
        ],
    )


@router.post(
    "/{course_id}/review/chat",
    response_model=CourseReviewChatMessage,
    summary="Gửi tin nhắn chat với agent (Admin)",
    responses={
        201: {"description": "Created"},
        403: {"description": "Không có quyền truy cập"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
async def send_chat_message(
    course_id: int,
    message_request: SendChatMessageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Gửi tin nhắn chat với agent trong quá trình review
    """
    # Kiểm tra course tồn tại
    course_result = await db.execute(select(Course).filter(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    try:
        # Lưu tin nhắn của admin
        admin_message = CourseReviewChat(
            course_id=course_id,
            user_id=admin_user.id,
            message=message_request.message,
            is_agent=False,
        )
        db.add(admin_message)
        await db.commit()
        await db.refresh(admin_message)

        # Gửi tin nhắn cho agent trong background
        background_tasks.add_task(
            process_agent_response, course_id, message_request.message, admin_user.id
        )

        return CourseReviewChatMessage.model_validate(admin_message)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi gửi tin nhắn: {str(e)}",
        )


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
    db: AsyncSession = Depends(get_async_db),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Approve draft content và lưu vào database chính
    """
    # Tìm course
    course_result = await db.execute(select(Course).filter(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khóa học với ID {course_id}",
        )

    # Tìm draft gần nhất
    draft_result = await db.execute(
        select(CourseDraft)
        .filter(CourseDraft.course_id == course_id, CourseDraft.status == "pending")
        .order_by(CourseDraft.created_at.desc())
        .limit(1)
    )
    draft = draft_result.scalar_one_or_none()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy draft pending cho khóa học này",
        )

    try:
        if approve_request.approved:
            # Parse agent content và lưu vào database
            agent_content = json.loads(draft.agent_content)
            await save_agent_content_to_db(course_id, agent_content, db)

            # Cập nhật status draft
            draft.status = "approved"

            # Lưu feedback nếu có
            if approve_request.feedback:
                feedback_message = CourseReviewChat(
                    course_id=course_id,
                    user_id=admin_user.id,
                    message=f"Approved with feedback: {approve_request.feedback}",
                    is_agent=False,
                )
                db.add(feedback_message)
        else:
            # Reject draft
            draft.status = "rejected"

            # Lưu feedback reject
            if approve_request.feedback:
                feedback_message = CourseReviewChat(
                    course_id=course_id,
                    user_id=admin_user.id,
                    message=f"Rejected with feedback: {approve_request.feedback}",
                    is_agent=False,
                )
                db.add(feedback_message)

        await db.commit()

        status_msg = "approved" if approve_request.approved else "rejected"
        return {"message": f"Draft đã được {status_msg} thành công"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi approve draft: {str(e)}",
        )


async def process_agent_response(course_id: int, user_message: str, user_id: int):
    """
    Xử lý phản hồi từ agent trong background
    """
    try:
        # TODO: Tích hợp với agent để xử lý tin nhắn
        # Hiện tại chỉ là mock response
        agent_response = f"Agent response to: {user_message}"

        async with get_independent_db_session() as session:
            # Lưu phản hồi agent
            agent_message = CourseReviewChat(
                course_id=course_id,
                user_id=user_id,  # Có thể tạo user_id đặc biệt cho agent
                message=agent_response,
                is_agent=True,
            )
            session.add(agent_message)
            await session.commit()

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error processing agent response: {str(e)}")


async def save_agent_content_to_db(
    course_id: int, agent_content: dict, db: AsyncSession
):
    """
    Lưu nội dung agent tạo ra vào database chính
    """
    # Parse và lưu topics
    for index, topic_data in enumerate(agent_content.get("topics", [])):
        # Tạo topic
        topic = Topic(
            course_id=course_id,
            name=topic_data.get("name"),
            description=topic_data.get("description"),
            prerequisites=topic_data.get("prerequisites", []),
            order=index + 1,  # Sắp xếp theo thứ tự trong list
        )
        db.add(topic)

    # Commit tất cả các thay đổi
    await db.commit()
