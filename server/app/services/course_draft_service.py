import asyncio

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database.database import get_async_db
from app.database.mongodb import get_mongo_collection
from app.models import CourseDraft, Course
from app.schemas import CourseCompositionRequestSchema
from app.schemas.course_draft_schema import CourseDraftSchema, TopicOrderRequest
from app.schemas.course_review_schema import ApproveDraftRequest
from app.services.course_generate_service import (
    get_course_generate_service,
    CourseGenerateService,
)
from app.services.course_service import save_course_from_draft


def get_course_draft_by_course_id(course_id: int) -> CourseDraftSchema:
    collection = get_mongo_collection("course_drafts")
    course_draft = collection.find_one({"course_id": course_id})
    if not course_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản nháp khóa học với ID {course_id}",
        )
    return CourseDraftSchema.model_validate(course_draft)


def update_or_create_course_draft(
    course_id: int, course_draft: CourseDraftSchema
) -> CourseDraftSchema:
    collection = get_mongo_collection("course_drafts")

    update_data = course_draft.model_dump(exclude_unset=True)
    update_data.pop("_id", None)

    result = collection.update_one(
        {"course_id": course_id},
        {"$set": update_data},
        upsert=True,
    )

    if result.upserted_id:
        doc = collection.find_one({"_id": result.upserted_id})
    else:
        doc = collection.find_one({"course_id": course_id})

    return CourseDraftSchema(**doc)


def reorder_topic_course_draft(
    topics: TopicOrderRequest,
    course_id: int = None,
):
    collection = get_mongo_collection("course_drafts")

    update_data = topics.model_dump(exclude_unset=True)

    result = collection.update_one(
        {"course_id": course_id},
        {"$set": {"topics": update_data["topics"]}},
    )

    return get_course_draft_by_course_id(course_id)


async def approve_course_draft_handler(
    course_id: int, approve_request: ApproveDraftRequest
):
    async with get_async_db() as db:
        course_generate_service: CourseGenerateService = get_course_generate_service()
        course_result = await db.execute(select(Course).filter(Course.id == course_id))
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với ID {course_id}",
            )

        draft_result = await db.execute(
            select(CourseDraft)
            .filter(CourseDraft.course_id == course_id)
            .order_by(CourseDraft.created_at.desc())
            .limit(1)
        )
        draft = draft_result.scalar_one_or_none()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy draft cho khóa học này",
            )

        try:
            if approve_request.approved:
                collection = get_mongo_collection("course_daft")
                course_draft = collection.find_one(
                    {
                        "course_id": course_id,
                        "session_id": draft.session_id,
                    }
                )
                await save_course_from_draft(course_draft)
            else:
                composition_request = CourseCompositionRequestSchema(
                    course_id=course_id,
                    course_title=course.title,
                    course_description=course.description,
                    course_level=course.level,
                    session_id=draft.session_id,
                    user_requirements=approve_request.feedback,
                )

                asyncio.create_task(
                    course_generate_service.background_create(composition_request)
                )

                return {
                    "message": "Draft đã được rejected và agent đang tái tạo nội dung"
                }

        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi approve draft: {str(e)}",
            )


class CourseDaftService:

    def __init__(self, db: AsyncSession):
        self.db = db


def get_course_draft_service(
    db: AsyncSession = Depends(get_async_db()),
) -> CourseDaftService:
    return CourseDaftService(db=db)
