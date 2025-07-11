from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lesson_model import Lesson, UserLesson
from app.models.topic_model import Topic
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.course_service import CourseService, get_course_service
from app.services.lesson_service import LessonService, get_lesson_service
from app.utils.utils import get_current_user
from app.utils.model_utils import convert_lesson_to_schema
from datetime import datetime

router = APIRouter(
    prefix="/lessons",
    tags=["Bài học"],
    responses={404: {"description": "Không tìm thấy bài học"}},
)


@router.get(
    "/{lesson_id}",
    responses={
        200: {"description": "Lấy thông tin bài học thành công"},
        404: {"description": "Không tìm thấy bài học"},
    },
)
async def get_lesson_by_id(
    lesson_id: int,
    db: Session = Depends(get_db),
    lesson_service: LessonService = Depends(get_lesson_service),
):
    """
    Lấy thông tin chi tiết của một bài học

    Args:
        lesson_id: ID của bài học
        db: Session database
        current_user: Thông tin người dùng hiện tại

    Returns:
        LessonResponseSchema: Thông tin chi tiết bài học

    Raises:
        HTTPException: Nếu không tìm thấy bài học
    """
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài học với ID {lesson_id}",
        )

    return lesson


@router.post(
    "/{lesson_id}/complete",
    responses={
        200: {"description": "Cập nhật trạng thái hoàn thành bài học thành công"},
        404: {"description": "Không tìm thấy bài học"},
        403: {"description": "Chưa đăng ký khóa học"},
    },
)
async def mark_lesson_completed(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Đánh dấu bài học đã hoàn thành

    Args:
        lesson_id: ID của bài học
        db: Session database
        current_user: Thông tin người dùng hiện tại

    Returns:
        dict: Thông báo kết quả

    Raises:
        HTTPException: Nếu không tìm thấy bài học hoặc chưa đăng ký khóa học
    """
    # Kiểm tra bài học có tồn tại không
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài học với ID {lesson_id}",
        )

    # Kiểm tra người dùng đã đăng ký khóa học chưa
    course_service = get_course_service()
    # Lấy course_id thông qua topic
    topic = db.query(Topic).filter(Topic.id == lesson.topic_id).first()
    if not topic or not topic.course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khóa học của bài học này",
        )

    if not course_service.is_enrolled(current_user.id, topic.course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học trước khi có thể hoàn thành bài học",
        )

    # Kiểm tra xem đã có UserLesson chưa
    user_lesson = (
        db.query(UserLesson)
        .filter(
            UserLesson.user_id == current_user.id, UserLesson.lesson_id == lesson_id
        )
        .first()
    )

    if user_lesson:
        # Cập nhật trạng thái
        user_lesson.is_completed = True
        user_lesson.progress = 100
        user_lesson.completed_at = datetime.utcnow()
    else:
        # Tạo mới UserLesson
        user_lesson = UserLesson(
            user_id=current_user.id,
            lesson_id=lesson_id,
            is_completed=True,
            progress=100,
            completed_at=datetime.utcnow(),
        )
        db.add(user_lesson)

    db.commit()

    return {"message": "Bài học đã được đánh dấu hoàn thành thành công"}


@router.delete(
    "/{lesson_id}/complete",
    responses={
        200: {"description": "Hủy trạng thái hoàn thành bài học thành công"},
        404: {"description": "Không tìm thấy bài học"},
    },
)
async def unmark_lesson_completed(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Hủy đánh dấu bài học đã hoàn thành

    Args:
        lesson_id: ID của bài học
        db: Session database
        current_user: Thông tin người dùng hiện tại

    Returns:
        dict: Thông báo kết quả

    Raises:
        HTTPException: Nếu không tìm thấy bài học
    """
    # Kiểm tra bài học có tồn tại không
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài học với ID {lesson_id}",
        )

    # Kiểm tra xem có UserLesson không
    user_lesson = (
        db.query(UserLesson)
        .filter(
            UserLesson.user_id == current_user.id, UserLesson.lesson_id == lesson_id
        )
        .first()
    )

    if user_lesson:
        # Cập nhật trạng thái
        user_lesson.is_completed = False
        user_lesson.progress = 0
        user_lesson.completed_at = None
        db.commit()

    return {"message": "Đã hủy trạng thái hoàn thành bài học"}


@router.get(
    "/{lesson_id}/status",
    responses={
        200: {"description": "Lấy trạng thái bài học thành công"},
        404: {"description": "Không tìm thấy bài học"},
    },
)
async def get_lesson_status(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy trạng thái hoàn thành của bài học

    Args:
        lesson_id: ID của bài học
        db: Session database
        current_user: Thông tin người dùng hiện tại

    Returns:
        dict: Trạng thái bài học

    Raises:
        HTTPException: Nếu không tìm thấy bài học
    """
    # Kiểm tra bài học có tồn tại không
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài học với ID {lesson_id}",
        )

    # Lấy trạng thái UserLesson
    user_lesson = (
        db.query(UserLesson)
        .filter(
            UserLesson.user_id == current_user.id, UserLesson.lesson_id == lesson_id
        )
        .first()
    )

    if user_lesson:
        return {
            "lesson_id": lesson_id,
            "is_completed": user_lesson.is_completed,
            "progress": user_lesson.progress,
            "completed_at": user_lesson.completed_at,
        }
    else:
        return {
            "lesson_id": lesson_id,
            "is_completed": False,
            "progress": 0,
            "completed_at": None,
        }
