from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal, get_async_db


class CourseDaftService:
    """
    Service để tạo nội dung khóa học dựa trên thông tin từ draft.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_course_daft_by_course_id(self, course_id: int):
        """
        Lấy thông tin draft của khóa học dựa trên ID khóa học.

        Args:
            course_id (int): ID của khóa học.

        Returns:
            dict: Thông tin draft của khóa học.
        """
        # Giả sử có một mô hình CourseDraft trong cơ sở dữ liệu
        result = await self.db.execute(select(CourseDaft))



def get_course_draft_service(db: AsyncSession = Depends(get_async_db())):
    """
    Trả về một instance của CourseDaftService.

    Returns:
        CourseDaftService: Instance của CourseDaftService.
    """
    return CourseDaftService(db=db)
