from typing import List

from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.database.database import get_independent_db_session
from app.models import Topic, Skill, Course
from app.models.course_model import CourseStatus
from app.services.course_draft_service import get_course_draft_by_course_id
from app.utils.model_utils import pydantic_to_sqlalchemy_scalar


async def approve_topic_draft_handler(course_id: int):
    course_draft = get_course_draft_by_course_id(course_id)
    if not course_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản nháp khóa học với ID {course_id}",
        )
    topic_list: List[Topic] = []
    for topic in course_draft.topics:
        topic_model = pydantic_to_sqlalchemy_scalar(topic, Topic)
        for skill in topic.skills:
            skill_model = pydantic_to_sqlalchemy_scalar(skill, Skill)
            skill_model.id = None
            topic_model.skills.append(skill_model)

        topic_model.course_id = course_id
        topic_model.id = None
        topic_list.append(topic_model)

    async with get_independent_db_session() as db:
        try:
            query_result = await db.execute(select(Course).filter(Course.id == course_id))
            course = query_result.scalar_one_or_none()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            if course.status == CourseStatus.APPROVED.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Topic đã được phê duyệt trước đó, không thể phê duyệt lại",
                )
            db.add_all(topic_list)
            course.status = CourseStatus.APPROVED
            # TODO: Hiện tại chỉ approve đến topic, sẽ có thêm lession....
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể phê duyệt bản nháp khóa học: đã có lỗi xảy ra",
            )

    return topic_list
