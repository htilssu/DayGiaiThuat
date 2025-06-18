from app.database.repository import Repository
from app.models.course_model import Course
from app.database.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


class CourseService:
    def __init__(self, repository: Repository[Course]):
        self.repository = repository

    async def get_course_by_id(self, course_id: int):
        return await self.repository.get_async(course_id)


def get_course_service(db: Session = Depends(get_db)):
    repository = Repository(Course, db)
    return CourseService(repository)
