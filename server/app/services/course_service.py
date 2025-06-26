from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.course_model import Course
from app.models.user_course_model import UserCourse
from app.models.user_model import User


class CourseService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_courses(self, skip: int = 0, limit: int = 10):
        """
        Lấy danh sách khóa học với phân trang

        Args:
            skip: Số lượng bản ghi bỏ qua
            limit: Số lượng bản ghi tối đa trả về

        Returns:
            List[Course]: Danh sách khóa học
        """
        return self.db.query(Course).offset(skip).limit(limit).all()

    def get_course(self, course_id: int):
        """
        Lấy thông tin chi tiết của một khóa học

        Args:
            course_id: ID của khóa học

        Returns:
            Course: Thông tin chi tiết của khóa học
        """
        return (
            self.db.query(Course)
            .filter(Course.id == course_id, Course.is_active == True)
            .first()
        )

    def create_course(self, course_data):
        """
        Tạo một khóa học mới

        Args:
            course_data: Dữ liệu để tạo khóa học

        Returns:
            Course: Thông tin của khóa học vừa tạo
        """
        try:
            # Tạo đối tượng Course từ dữ liệu đầu vào
            new_course = Course(**course_data.dict())

            # Thêm vào database
            self.db.add(new_course)
            self.db.commit()
            self.db.refresh(new_course)

            return new_course
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi tạo khóa học: {str(e)}",
            )

    def update_course(self, course_id: int, course_data):
        """
        Cập nhật thông tin một khóa học

        Args:
            course_id: ID của khóa học cần cập nhật
            course_data: Dữ liệu cập nhật

        Returns:
            Course: Thông tin khóa học sau khi cập nhật
        """
        try:
            # Tìm khóa học cần cập nhật
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Cập nhật thông tin khóa học từ dữ liệu đầu vào
            course_dict = course_data.dict(exclude_unset=True)
            for key, value in course_dict.items():
                setattr(course, key, value)

            # Lưu thay đổi vào database
            self.db.commit()
            self.db.refresh(course)

            return course
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật khóa học: {str(e)}",
            )

    def delete_course(self, course_id: int):
        """
        Xóa một khóa học

        Args:
            course_id: ID của khóa học cần xóa

        Returns:
            bool: True nếu xóa thành công
        """
        try:
            # Tìm khóa học cần xóa
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Xóa khóa học
            self.db.delete(course)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa khóa học: {str(e)}",
            )

    def enroll_course(self, user_id: int, course_id: int):
        """
        Đăng ký khóa học cho người dùng

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            UserCourse: Thông tin đăng ký khóa học
        """
        try:
            # Kiểm tra xem người dùng có tồn tại không
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy người dùng với ID {user_id}",
                )

            # Kiểm tra xem khóa học có tồn tại không
            course = self.get_course(course_id)
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy khóa học với ID {course_id}",
                )

            # Kiểm tra xem người dùng đã đăng ký khóa học này chưa
            existing_enrollment = (
                self.db.query(UserCourse)
                .filter(
                    and_(
                        UserCourse.user_id == user_id, UserCourse.course_id == course_id
                    )
                )
                .first()
            )

            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người dùng đã đăng ký khóa học này",
                )

            # Tạo đăng ký mới
            enrollment = UserCourse(user_id=user_id, course_id=course_id)
            self.db.add(enrollment)
            self.db.commit()
            self.db.refresh(enrollment)

            return enrollment
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi đăng ký khóa học: {str(e)}",
            )

    def unenroll_course(self, user_id: int, course_id: int):
        """
        Hủy đăng ký khóa học của người dùng

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            bool: True nếu hủy đăng ký thành công
        """
        try:
            # Tìm đăng ký cần hủy
            enrollment = (
                self.db.query(UserCourse)
                .filter(
                    and_(
                        UserCourse.user_id == user_id, UserCourse.course_id == course_id
                    )
                )
                .first()
            )

            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy đăng ký khóa học",
                )

            # Xóa đăng ký
            self.db.delete(enrollment)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi hủy đăng ký khóa học: {str(e)}",
            )

    def get_user_courses(self, user_id: int):
        """
        Lấy danh sách khóa học mà người dùng đã đăng ký

        Args:
            user_id: ID của người dùng

        Returns:
            List[Course]: Danh sách khóa học
        """
        try:
            # Kiểm tra xem người dùng có tồn tại không
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy người dùng với ID {user_id}",
                )

            # Lấy danh sách khóa học mà người dùng đã đăng ký
            enrollments = (
                self.db.query(UserCourse).filter(UserCourse.user_id == user_id).all()
            )
            course_ids = [enrollment.course_id for enrollment in enrollments]
            courses = self.db.query(Course).filter(Course.id.in_(course_ids)).all()

            return courses
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi lấy danh sách khóa học: {str(e)}",
            )

    def is_enrolled(self, user_id: int, course_id: int):
        """
        Kiểm tra xem người dùng đã đăng ký khóa học chưa

        Args:
            user_id: ID của người dùng
            course_id: ID của khóa học

        Returns:
            bool: True nếu người dùng đã đăng ký khóa học
        """
        enrollment = (
            self.db.query(UserCourse)
            .filter(
                and_(UserCourse.user_id == user_id, UserCourse.course_id == course_id)
            )
            .first()
        )
        return enrollment is not None


def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)
