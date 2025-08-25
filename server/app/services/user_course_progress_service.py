from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import Depends, HTTPException, status

from app.database.database import get_async_db
from app.models.user_lesson_model import UserLesson
from app.schemas.user_course_progress_schema import (
    UserLessonCreate,
    UserLessonUpdate,
    UserLessonResponse,
    CourseProgressSummary,
)


class UserLessonService:
    pass
