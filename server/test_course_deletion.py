#!/usr/bin/env python3
"""
Test script để kiểm tra việc xóa course có cascade delete đúng không
"""

import asyncio
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.course_model import Course
from app.models.topic_model import Topic
from app.models.lesson_model import Lesson, LessonSection
from app.services.course_service import CourseService


def test_course_cascade_delete():
    """
    Test function to check if course deletion properly cascades to topics, lessons, and sections
    """
    db = next(get_db())

    try:
        # Tìm một course có topics và lessons để test
        course_with_content = db.query(Course).join(Topic).join(Lesson).first()

        if not course_with_content:
            print("Không tìm thấy course nào có topics và lessons để test")
            return

        course_id = course_with_content.id
        print(
            f"Testing deletion for Course ID: {course_id} - '{course_with_content.title}'"
        )

        # Đếm số lượng topics, lessons, sections trước khi xóa
        topics_before = db.query(Topic).filter(Topic.course_id == course_id).count()
        lessons_before = (
            db.query(Lesson).join(Topic).filter(Topic.course_id == course_id).count()
        )
        sections_before = (
            db.query(LessonSection)
            .join(Lesson)
            .join(Topic)
            .filter(Topic.course_id == course_id)
            .count()
        )

        print(f"Trước khi xóa:")
        print(f"  - Topics: {topics_before}")
        print(f"  - Lessons: {lessons_before}")
        print(f"  - Lesson Sections: {sections_before}")

        # Sử dụng course service để xóa (với logic validation)
        course_service = CourseService(db)
        result = course_service.bulk_delete_courses([course_id])

        print(f"Kết quả xóa:")
        print(f"  - Deleted count: {result['deleted_count']}")
        print(f"  - Failed count: {result['failed_count']}")
        print(f"  - Errors: {result['errors']}")
        print(f"  - Deleted items: {result['deleted_items']}")

        # Kiểm tra sau khi xóa
        topics_after = db.query(Topic).filter(Topic.course_id == course_id).count()
        lessons_after = (
            db.query(Lesson).join(Topic).filter(Topic.course_id == course_id).count()
        )
        sections_after = (
            db.query(LessonSection)
            .join(Lesson)
            .join(Topic)
            .filter(Topic.course_id == course_id)
            .count()
        )

        print(f"Sau khi xóa:")
        print(f"  - Topics: {topics_after}")
        print(f"  - Lessons: {lessons_after}")
        print(f"  - Lesson Sections: {sections_after}")

        if topics_after == 0 and lessons_after == 0 and sections_after == 0:
            print("✅ CASCADE DELETE hoạt động đúng!")
        else:
            print("❌ CASCADE DELETE không hoạt động như mong đợi!")

    except Exception as e:
        print(f"Lỗi khi test: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=== TEST COURSE CASCADE DELETE ===")
    test_course_cascade_delete()
