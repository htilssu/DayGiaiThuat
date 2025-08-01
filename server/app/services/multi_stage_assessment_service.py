import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from fastapi import Depends

from app.core.agents.multi_stage_assessment_agent import (
    MultiStageAssessmentAgent,
    get_multi_stage_assessment_agent,
)
from app.schemas.multi_stage_assessment_schema import (
    AssessmentType,
    AssessmentTrigger,
    MultiStageAssessmentRequest,
    ComprehensiveAssessmentResponse,
    AssessmentHistory,
    LearnerProfile,
)
from app.models.user_model import User
from app.models.test_session import TestSession
from app.models.user_course_progress_model import UserCourseProgress, ProgressStatus
from app.database.database import get_async_db

logger = logging.getLogger(__name__)


class MultiStageAssessmentService:
    """Service quản lý đánh giá đa giai đoạn trong hành trình học tập"""

    def __init__(
        self, session: AsyncSession, assessment_agent: MultiStageAssessmentAgent
    ):
        self.session = session
        self.assessment_agent = assessment_agent

        # Cache cho learner profiles
        self._learner_profiles_cache = {}
        self._cache_ttl = 300  # 5 minutes

    async def conduct_assessment(
        self, request: MultiStageAssessmentRequest
    ) -> ComprehensiveAssessmentResponse:
        """
        Thực hiện đánh giá theo yêu cầu

        Args:
            request: Yêu cầu đánh giá

        Returns:
            ComprehensiveAssessmentResponse: Kết quả đánh giá
        """
        try:
            logger.info(
                f"Conducting {request.assessment_type} assessment for user {request.user_id}"
            )

            # Prepare agent parameters
            agent_params = {
                "assessment_type": request.assessment_type,
                "user_id": request.user_id,
                "trigger": request.trigger,
                "context_data": request.context_data,
            }

            # Add specific parameters based on assessment type
            if request.course_id:
                agent_params["course_id"] = request.course_id
            if request.lesson_id:
                agent_params["lesson_id"] = request.lesson_id
            if request.test_session_id:
                agent_params["test_session_id"] = request.test_session_id

            # Conduct assessment
            result = await self.assessment_agent.act(**agent_params)

            # Update cache
            self._update_learner_profile_cache(
                request.user_id, result.updated_learner_profile
            )

            # Log assessment
            await self._log_assessment_event(request, result)

            logger.info(
                f"Completed {request.assessment_type} assessment for user {request.user_id}"
            )
            return result

        except Exception as e:
            logger.error(f"Error conducting assessment: {e}")
            raise

    async def trigger_automatic_assessment(
        self,
        user_id: int,
        trigger: AssessmentTrigger,
        context_data: Dict[str, Any] = None,
    ) -> Optional[ComprehensiveAssessmentResponse]:
        """
        Kích hoạt đánh giá tự động dựa trên trigger

        Args:
            user_id: ID người dùng
            trigger: Tình huống kích hoạt
            context_data: Dữ liệu ngữ cảnh

        Returns:
            ComprehensiveAssessmentResponse hoặc None nếu không cần đánh giá
        """
        try:
            # Determine assessment type based on trigger
            assessment_type = self._get_assessment_type_for_trigger(trigger)
            if not assessment_type:
                return None

            # Check if assessment is needed
            if not await self._should_conduct_assessment(
                user_id, assessment_type, trigger
            ):
                logger.debug(
                    f"Assessment not needed for user {user_id}, trigger {trigger}"
                )
                return None

            # Create assessment request
            request = MultiStageAssessmentRequest(
                user_id=user_id,
                assessment_type=assessment_type,
                trigger=trigger,
                context_data=context_data or {},
            )

            # Add context-specific data
            if trigger == AssessmentTrigger.COURSE_START:
                request.course_id = (
                    context_data.get("course_id") if context_data else None
                )
            elif trigger == AssessmentTrigger.LESSON_COMPLETE:
                request.lesson_id = (
                    context_data.get("lesson_id") if context_data else None
                )

            return await self.conduct_assessment(request)

        except Exception as e:
            logger.error(f"Error in automatic assessment trigger: {e}")
            return None

    async def get_learner_profile(
        self, user_id: int, force_refresh: bool = False
    ) -> LearnerProfile:
        """
        Lấy hồ sơ người học

        Args:
            user_id: ID người dùng
            force_refresh: Buộc cập nhật từ database

        Returns:
            LearnerProfile: Hồ sơ người học
        """
        try:
            # Check cache first
            if not force_refresh and user_id in self._learner_profiles_cache:
                cached_data = self._learner_profiles_cache[user_id]
                if (
                    datetime.utcnow() - cached_data["timestamp"]
                ).seconds < self._cache_ttl:
                    return cached_data["profile"]

            # Generate fresh profile
            profile = await self._generate_learner_profile(user_id)

            # Update cache
            self._update_learner_profile_cache(user_id, profile)

            return profile

        except Exception as e:
            logger.error(f"Error getting learner profile: {e}")
            raise

    async def get_assessment_history(
        self, user_id: int, limit: int = 50
    ) -> AssessmentHistory:
        """
        Lấy lịch sử đánh giá của người dùng

        Args:
            user_id: ID người dùng
            limit: Số lượng đánh giá tối đa

        Returns:
            AssessmentHistory: Lịch sử đánh giá
        """
        try:
            # Note: Trong thực tế, sẽ query từ bảng assessment_history
            # Hiện tại tạo mock data

            # Get basic learning data
            user_history = await self.assessment_agent._get_user_learning_history(
                user_id
            )

            # Create mock assessment history
            assessments = []
            for i in range(min(limit, 10)):  # Mock 10 assessments
                assessment = ComprehensiveAssessmentResponse(
                    user_id=user_id,
                    assessment_type=AssessmentType.FORMATIVE,
                    timestamp=datetime.utcnow() - timedelta(days=i * 7),
                    updated_learner_profile=await self.get_learner_profile(user_id),
                    execution_time=2.5,
                    data_quality_score=0.85,
                    recommendations_count=3,
                )
                assessments.append(assessment)

            # Analyze trends
            learning_trajectory = []
            performance_trends = {}

            scores = user_history.get("test_trend", [])
            if scores:
                performance_trends["test_scores"] = scores

                for i, score in enumerate(scores):
                    learning_trajectory.append(
                        {
                            "week": i + 1,
                            "score": score,
                            "trend": (
                                "improving"
                                if i > 0 and score > scores[i - 1]
                                else "stable"
                            ),
                        }
                    )

            return AssessmentHistory(
                user_id=user_id,
                assessments=assessments,
                learning_trajectory=learning_trajectory,
                performance_trends=performance_trends,
                total_assessments=len(assessments),
                average_improvement=5.2,  # Mock data
                consistency_score=user_history.get("learning_consistency", 0.7),
            )

        except Exception as e:
            logger.error(f"Error getting assessment history: {e}")
            raise

    async def recommend_next_assessment(self, user_id: int) -> Dict[str, Any]:
        """
        Đề xuất đánh giá tiếp theo

        Args:
            user_id: ID người dùng

        Returns:
            Dict với thông tin đề xuất đánh giá
        """
        try:
            # Get current learner profile
            profile = await self.get_learner_profile(user_id)

            # Get recent activity
            recent_progress = await self.session.execute(
                select(UserCourseProgress)
                .where(
                    UserCourseProgress.user_course_id.in_(
                        select(UserCourseProgress.user_course_id)
                        .join(UserCourseProgress.user_course)
                        .where(UserCourseProgress.user_course.has(user_id=user_id))
                    )
                )
                .where(
                    UserCourseProgress.last_viewed_at
                    >= datetime.utcnow() - timedelta(days=7)
                )
                .order_by(desc(UserCourseProgress.last_viewed_at))
            )

            recent_activities = recent_progress.scalars().all()

            # Determine recommendation
            recommendations = []

            # Check for formative assessment
            if len(recent_activities) >= 3:
                recommendations.append(
                    {
                        "type": AssessmentType.FORMATIVE,
                        "reason": "Regular progress check based on recent activity",
                        "priority": "medium",
                        "estimated_time": 5,
                        "trigger": AssessmentTrigger.LEARNING_PATTERN_CHANGE,
                    }
                )

            # Check for continuous assessment
            last_assessment_time = datetime.utcnow() - timedelta(days=3)  # Mock
            if (datetime.utcnow() - last_assessment_time).days >= 7:
                recommendations.append(
                    {
                        "type": AssessmentType.CONTINUOUS,
                        "reason": "Weekly continuous assessment",
                        "priority": "low",
                        "estimated_time": 2,
                        "trigger": AssessmentTrigger.MANUAL_REQUEST,
                    }
                )

            # Check engagement level
            if profile.engagement_patterns.get("engagement_type") == "low_engagement":
                recommendations.append(
                    {
                        "type": AssessmentType.CONTINUOUS,
                        "reason": "Low engagement detected - intervention assessment needed",
                        "priority": "high",
                        "estimated_time": 3,
                        "trigger": AssessmentTrigger.IDLE_DETECTION,
                    }
                )

            return {
                "user_id": user_id,
                "recommendations": recommendations,
                "next_scheduled": recommendations[0] if recommendations else None,
                "generated_at": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Error recommending next assessment: {e}")
            raise

    async def schedule_assessment(
        self, user_id: int, assessment_type: AssessmentType, scheduled_time: datetime
    ) -> Dict[str, Any]:
        """
        Lên lịch đánh giá

        Args:
            user_id: ID người dùng
            assessment_type: Loại đánh giá
            scheduled_time: Thời gian lên lịch

        Returns:
            Dict với thông tin lịch trình
        """
        try:
            # Note: Trong thực tế sẽ lưu vào bảng assessment_schedules
            schedule_data = {
                "user_id": user_id,
                "assessment_type": assessment_type,
                "scheduled_time": scheduled_time,
                "status": "scheduled",
                "created_at": datetime.utcnow(),
            }

            logger.info(
                f"Scheduled {assessment_type} assessment for user {user_id} at {scheduled_time}"
            )
            return schedule_data

        except Exception as e:
            logger.error(f"Error scheduling assessment: {e}")
            raise

    # Helper methods
    def _get_assessment_type_for_trigger(
        self, trigger: AssessmentTrigger
    ) -> Optional[AssessmentType]:
        """Xác định loại đánh giá dựa trên trigger"""
        trigger_mapping = {
            AssessmentTrigger.COURSE_START: AssessmentType.INITIAL,
            AssessmentTrigger.LESSON_COMPLETE: AssessmentType.FORMATIVE,
            AssessmentTrigger.QUIZ_SUBMIT: AssessmentType.FORMATIVE,
            AssessmentTrigger.CHAPTER_END: AssessmentType.FORMATIVE,
            AssessmentTrigger.COURSE_END: AssessmentType.SUMMATIVE,
            AssessmentTrigger.IDLE_DETECTION: AssessmentType.CONTINUOUS,
            AssessmentTrigger.LEARNING_PATTERN_CHANGE: AssessmentType.CONTINUOUS,
            AssessmentTrigger.MANUAL_REQUEST: AssessmentType.CONTINUOUS,
        }
        return trigger_mapping.get(trigger)

    async def _should_conduct_assessment(
        self, user_id: int, assessment_type: AssessmentType, trigger: AssessmentTrigger
    ) -> bool:
        """Kiểm tra xem có nên thực hiện đánh giá không"""
        try:
            # Check frequency limits
            if assessment_type == AssessmentType.CONTINUOUS:
                # Limit continuous assessments to once per hour
                # In real implementation, check last assessment time from database
                return True  # Simplified for now

            elif assessment_type == AssessmentType.FORMATIVE:
                # Limit formative assessments to once per day
                return True  # Simplified for now

            elif assessment_type == AssessmentType.INITIAL:
                # Only one initial assessment per course
                return True  # Check if already done for this course

            elif assessment_type == AssessmentType.SUMMATIVE:
                # Only at course completion
                return True  # Check course completion status

            return True

        except Exception as e:
            logger.error(f"Error checking assessment necessity: {e}")
            return False

    async def _generate_learner_profile(self, user_id: int) -> LearnerProfile:
        """Tạo hồ sơ người học từ dữ liệu hiện có"""
        try:
            # Get learning data
            behavior_data = await self.assessment_agent._get_learning_behavior_data(
                user_id
            )
            patterns = await self.assessment_agent._detect_learning_patterns(
                behavior_data
            )
            user_history = await self.assessment_agent._get_user_learning_history(
                user_id
            )

            # Determine current level
            avg_score = user_history.get("average_score", 0)
            if avg_score >= 80:
                current_level = "advanced"
            elif avg_score >= 60:
                current_level = "intermediate"
            else:
                current_level = "beginner"

            # Build knowledge map (mock data)
            knowledge_map = {
                "algorithms": min(avg_score / 100, 1.0),
                "data_structures": min((avg_score - 5) / 100, 1.0),
                "problem_solving": min((avg_score + 5) / 100, 1.0),
            }

            # Identify skill gaps
            skill_gaps = [
                topic for topic, score in knowledge_map.items() if score < 0.6
            ]

            return LearnerProfile(
                user_id=user_id,
                current_level=current_level,
                knowledge_map=knowledge_map,
                skill_gaps=skill_gaps,
                learning_style={"visual": 0.7, "auditory": 0.3, "kinesthetic": 0.5},
                preferred_content_types=["video", "practice", "text"],
                optimal_session_duration=45,
                engagement_patterns=patterns,
                performance_trends=[
                    {"period": "last_week", "score": avg_score},
                    {"period": "last_month", "score": max(0, avg_score - 5)},
                ],
                last_updated=datetime.utcnow(),
                confidence_score=0.8,
            )

        except Exception as e:
            logger.error(f"Error generating learner profile: {e}")
            raise

    def _update_learner_profile_cache(self, user_id: int, profile: LearnerProfile):
        """Cập nhật cache hồ sơ người học"""
        self._learner_profiles_cache[user_id] = {
            "profile": profile,
            "timestamp": datetime.utcnow(),
        }

    async def _log_assessment_event(
        self,
        request: MultiStageAssessmentRequest,
        result: ComprehensiveAssessmentResponse,
    ):
        """Ghi log sự kiện đánh giá"""
        try:
            # In real implementation, save to assessment_logs table
            log_data = {
                "user_id": request.user_id,
                "assessment_type": request.assessment_type,
                "trigger": request.trigger,
                "execution_time": result.execution_time,
                "data_quality_score": result.data_quality_score,
                "recommendations_count": result.recommendations_count,
                "timestamp": result.timestamp,
            }

            logger.info(f"Assessment logged: {log_data}")

        except Exception as e:
            logger.error(f"Error logging assessment event: {e}")

    async def get_assessment_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy analytics đánh giá cho người dùng

        Args:
            user_id: ID người dùng

        Returns:
            Dict với analytics data
        """
        try:
            # Get assessment history
            history = await self.get_assessment_history(user_id)

            # Calculate analytics
            total_assessments = history.total_assessments
            assessment_types_count = {}

            for assessment in history.assessments:
                assessment_type = assessment.assessment_type
                if assessment_type not in assessment_types_count:
                    assessment_types_count[assessment_type] = 0
                assessment_types_count[assessment_type] += 1

            # Performance trends
            performance_data = history.performance_trends.get("test_scores", [])

            analytics = {
                "user_id": user_id,
                "summary": {
                    "total_assessments": total_assessments,
                    "assessment_types": assessment_types_count,
                    "average_improvement": history.average_improvement,
                    "consistency_score": history.consistency_score,
                },
                "performance": {
                    "current_score": performance_data[-1] if performance_data else 0,
                    "trend": (
                        "improving"
                        if len(performance_data) >= 2
                        and performance_data[-1] > performance_data[-2]
                        else "stable"
                    ),
                    "best_score": max(performance_data) if performance_data else 0,
                    "improvement_rate": history.average_improvement,
                },
                "recommendations": {
                    "next_assessment": await self.recommend_next_assessment(user_id),
                    "focus_areas": await self._get_focus_areas(user_id),
                },
                "generated_at": datetime.utcnow(),
            }

            return analytics

        except Exception as e:
            logger.error(f"Error getting assessment analytics: {e}")
            raise

    async def _get_focus_areas(self, user_id: int) -> List[Dict[str, Any]]:
        """Lấy các khu vực cần tập trung"""
        try:
            profile = await self.get_learner_profile(user_id)

            focus_areas = []
            for gap in profile.skill_gaps:
                focus_areas.append(
                    {
                        "area": gap,
                        "current_level": profile.knowledge_map.get(gap, 0),
                        "target_level": 0.8,
                        "priority": (
                            "high"
                            if profile.knowledge_map.get(gap, 0) < 0.4
                            else "medium"
                        ),
                    }
                )

            return focus_areas

        except Exception as e:
            logger.error(f"Error getting focus areas: {e}")
            return []


def get_multi_stage_assessment_service(
    session: AsyncSession = Depends(get_async_db),
    assessment_agent: MultiStageAssessmentAgent = Depends(
        get_multi_stage_assessment_agent
    ),
) -> MultiStageAssessmentService:
    """Dependency injection cho MultiStageAssessmentService"""
    return MultiStageAssessmentService(session, assessment_agent)
