"""
Service để quản lý việc phân tích điểm yếu và mạnh của người dùng
"""

import asyncio
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agents.assessment_agent import AssessmentAgent
from app.database.database import get_async_db, get_independent_db_session
from app.models.user_assessment_model import UserAssessment
from app.models.test_session import TestSession
from app.models.user_model import User
from app.schemas.user_assessment_schema import (
    UserAssessmentCreate,
    UserAssessmentUpdate,
    UserAssessmentResponse,
    AssessmentAnalysisRequest,
)

logger = logging.getLogger(__name__)


class UserAssessmentService:
    """Service để quản lý đánh giá người dùng"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger

    async def create_assessment(
        self, assessment_data: UserAssessmentCreate
    ) -> UserAssessmentResponse:
        """
        Tạo một đánh giá mới cho người dùng

        Args:
            assessment_data: Dữ liệu đánh giá

        Returns:
            UserAssessmentResponse: Đánh giá đã được tạo
        """
        try:
            # Kiểm tra xem đã có assessment cho test session này chưa
            existing_result = await self.db.execute(
                select(UserAssessment).filter(
                    UserAssessment.test_session_id == assessment_data.test_session_id
                )
            )
            existing_assessment = existing_result.scalar_one_or_none()

            if existing_assessment:
                # Cập nhật assessment hiện có
                for field, value in assessment_data.model_dump(
                    exclude_unset=True
                ).items():
                    if hasattr(existing_assessment, field):
                        setattr(existing_assessment, field, value)

                await self.db.commit()
                await self.db.refresh(existing_assessment)
                return UserAssessmentResponse.model_validate(existing_assessment)
            else:
                # Tạo assessment mới
                assessment = UserAssessment(**assessment_data.model_dump())
                self.db.add(assessment)
                await self.db.commit()
                await self.db.refresh(assessment)
                return UserAssessmentResponse.model_validate(assessment)

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Lỗi khi tạo đánh giá: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi tạo đánh giá: {str(e)}",
            )

    async def get_assessment_by_test_session(
        self, test_session_id: str
    ) -> Optional[UserAssessmentResponse]:
        """
        Lấy đánh giá theo test session ID

        Args:
            test_session_id: ID của phiên thi

        Returns:
            UserAssessmentResponse hoặc None nếu không tìm thấy
        """
        result = await self.db.execute(
            select(UserAssessment).filter(
                UserAssessment.test_session_id == test_session_id
            )
        )
        assessment = result.scalar_one_or_none()

        if assessment:
            return UserAssessmentResponse.model_validate(assessment)
        return None

    async def get_user_assessments(
        self, user_id: int, limit: int = 10
    ) -> list[UserAssessmentResponse]:
        """
        Lấy danh sách đánh giá của người dùng

        Args:
            user_id: ID của người dùng
            limit: Số lượng đánh giá tối đa

        Returns:
            Danh sách UserAssessmentResponse
        """
        result = await self.db.execute(
            select(UserAssessment)
            .filter(UserAssessment.user_id == user_id)
            .order_by(UserAssessment.created_at.desc())
            .limit(limit)
        )
        assessments = result.scalars().all()

        return [
            UserAssessmentResponse.model_validate(assessment)
            for assessment in assessments
        ]

    async def analyze_user_weaknesses_background(
        self, analysis_request: AssessmentAnalysisRequest
    ) -> None:
        """
        Phân tích điểm yếu của người dùng trong background sau khi submit bài test

        Args:
            analysis_request: Request chứa thông tin để phân tích
        """

        async def run_analysis_task():
            try:
                # Sử dụng session độc lập cho background task
                async with get_independent_db_session() as independent_db:
                    service = UserAssessmentService(independent_db)

                    # Lấy thông tin test session
                    test_session_result = await independent_db.execute(
                        select(TestSession).filter(
                            TestSession.id == analysis_request.test_session_id
                        )
                    )
                    test_session = test_session_result.scalar_one_or_none()

                    if not test_session:
                        self.logger.error(
                            f"Không tìm thấy test session: {analysis_request.test_session_id}"
                        )
                        return

                    # Kiểm tra xem test session đã được submit chưa
                    if not test_session.is_submitted:
                        self.logger.warning(
                            f"Test session chưa được submit: {analysis_request.test_session_id}"
                        )
                        return

                    # Khởi tạo Assessment Agent với các dependencies cần thiết
                    from app.services.test_service import TestService
                    from app.services.course_service import CourseService

                    test_service = TestService(independent_db)
                    course_service = CourseService(independent_db)
                    assessment_agent = AssessmentAgent(
                        test_service, course_service, independent_db
                    )

                    # Chạy phân tích với agent
                    self.logger.info(
                        f"Bắt đầu phân tích điểm yếu cho user {analysis_request.user_id}"
                    )

                    analysis_result = await assessment_agent.act(
                        assessment_type="test",
                        test_session_id=analysis_request.test_session_id,
                        user_id=analysis_request.user_id,
                    )

                    # Xử lý kết quả analysis một cách an toàn
                    try:
                        # Thử truy xuất thông tin từ analysis_result
                        strengths = getattr(analysis_result, "strengths", [])
                        weaknesses = getattr(analysis_result, "weaknesses", [])
                        recommendations = getattr(
                            analysis_result, "recommendations", []
                        )

                        # Chuyển đổi sang dict để lưu
                        raw_data = {}
                        if hasattr(analysis_result, "model_dump"):
                            raw_data = analysis_result.model_dump()
                        else:
                            raw_data = {"type": str(type(analysis_result))}

                    except Exception as extract_error:
                        self.logger.warning(
                            f"Lỗi khi trích xuất dữ liệu analysis: {extract_error}"
                        )
                        strengths = []
                        weaknesses = []
                        recommendations = []
                        raw_data = {"error": str(extract_error)}

                    assessment_data = UserAssessmentCreate(
                        user_id=analysis_request.user_id,
                        test_session_id=analysis_request.test_session_id,
                        course_id=analysis_request.course_id,
                        strengths={"items": strengths},
                        weaknesses={"items": weaknesses},
                        recommendations={"items": recommendations},
                        skill_levels={},
                        learning_path={},
                        overall_score=None,
                        proficiency_level=None,
                        analysis_summary="Phân tích điểm yếu dựa trên kết quả bài kiểm tra đầu vào",
                        raw_analysis=raw_data,
                    )

                    # Lưu đánh giá vào database
                    await service.create_assessment(assessment_data)

                    self.logger.info(
                        f"✅ Hoàn thành phân tích điểm yếu cho user {analysis_request.user_id}"
                    )

            except Exception as e:
                self.logger.error(f"❌ Lỗi khi phân tích điểm yếu: {e}", exc_info=True)

        # Chạy background task
        asyncio.create_task(run_analysis_task())

    async def update_assessment(
        self, assessment_id: int, update_data: UserAssessmentUpdate
    ) -> UserAssessmentResponse:
        """
        Cập nhật đánh giá

        Args:
            assessment_id: ID của đánh giá
            update_data: Dữ liệu cập nhật

        Returns:
            UserAssessmentResponse: Đánh giá đã được cập nhật
        """
        try:
            result = await self.db.execute(
                select(UserAssessment).filter(UserAssessment.id == assessment_id)
            )
            assessment = result.scalar_one_or_none()

            if not assessment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy đánh giá với ID {assessment_id}",
                )

            # Cập nhật các field
            for field, value in update_data.model_dump(exclude_unset=True).items():
                if hasattr(assessment, field):
                    setattr(assessment, field, value)

            await self.db.commit()
            await self.db.refresh(assessment)

            return UserAssessmentResponse.model_validate(assessment)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Lỗi khi cập nhật đánh giá: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi cập nhật đánh giá: {str(e)}",
            )


async def get_user_assessment_service(
    db: AsyncSession = Depends(get_async_db),
) -> UserAssessmentService:
    """Dependency để inject UserAssessmentService"""
    return UserAssessmentService(db)
