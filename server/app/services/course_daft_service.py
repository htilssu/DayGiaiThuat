from fastapi import Depends
from pymongo import ASCENDING
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal, get_async_db
from app.database.mongodb import get_mongo_collection
from app.schemas.course_draft_schema import CourseDraftSchemaWithId


async def get_course_daft_by_course_id(course_id: int) -> list[CourseDraftSchemaWithId]:
    collection = get_mongo_collection("course_drafts")
    course_draft = collection.find({"course_id": course_id}).sort("created_at", ASCENDING)
    course_daft_list = [
        CourseDraftSchemaWithId(**draft) for draft in course_draft.to_list()
    ]
    return course_daft_list


class CourseDaftService:

    def __init__(self, db: AsyncSession):
        self.db = db


def get_course_draft_service(db: AsyncSession = Depends(get_async_db())) -> CourseDaftService:
    return CourseDaftService(db=db)
