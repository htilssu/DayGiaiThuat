from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database.database import get_async_db
from app.database.mongodb import get_mongo_collection
from app.schemas.course_draft_schema import CourseDraftSchema


def get_course_daft_by_course_id(course_id: int) -> CourseDraftSchema:
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


class CourseDaftService:

    def __init__(self, db: AsyncSession):
        self.db = db


def get_course_draft_service(
        db: AsyncSession = Depends(get_async_db()),
) -> CourseDaftService:
    return CourseDaftService(db=db)
