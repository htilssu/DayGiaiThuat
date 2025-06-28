import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agents.assessment_agent import get_assessment_agent, AssessmentAgent
from app.database.database import get_async_session
from app.schemas.assessment_schema import AssessmentRequest, AssessmentResultResponse
from app.services.test_service import TestService, get_test_service
from app.utils.utils import get_current_user
from app.models.user_model import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post(
    "/analyze-test-session",
    response_model=AssessmentResultResponse,
    summary="Đánh giá trình độ học viên dựa trên kết quả bài kiểm tra",
    description="""
    Endpoint này sử dụng AssessmentAgent để phân tích kết quả bài kiểm tra đầu vào của học viên và:
    
    1. **Đánh giá trình độ hiện tại**: Xác định mức độ beginner/intermediate/advanced
    2. **Phân tích điểm mạnh/yếu**: Chi tiết theo từng chủ đề trong khóa học  
    3. **Tạo lộ trình học tập**: Sắp xếp thứ tự học các chủ đề dựa trên kết quả đánh giá
    4. **Đưa ra gợi ý**: Phương pháp học và các bước tiếp theo
    
    **Yêu cầu**: 
    - Test session phải đã hoàn thành (status = "completed", is_submitted = true)
    - Người dùng phải có quyền truy cập test session này
    
    **Kết quả trả về**:
    - Điểm số tổng thể và từng chủ đề
    - Lộ trình học tập được cá nhân hóa
    - Gợi ý cải thiện cụ thể
    """,
)
async def analyze_test_session(
    request: AssessmentRequest,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service),
    assessment_agent: AssessmentAgent = Depends(get_assessment_agent),
    session: AsyncSession = Depends(get_async_session),
) -> AssessmentResultResponse:
    """
    Phân tích kết quả bài kiểm tra đầu vào và tạo lộ trình học tập cá nhân hóa

    Args:
        request: Thông tin request chứa test_session_id
        current_user: Thông tin người dùng hiện tại (từ authentication)
        test_service: Service để xử lý logic liên quan đến test
        assessment_agent: Agent AI để đánh giá trình độ
        session: Database session

    Returns:
        AssessmentResultResponse: Kết quả đánh giá và lộ trình học tập

    Raises:
        HTTPException:
            - 404: Không tìm thấy test session
            - 403: Không có quyền truy cập test session
            - 400: Test session chưa hoàn thành
            - 500: Lỗi trong quá trình đánh giá
    """
    try:
        # 1. Kiểm tra test session có tồn tại không
        test_session = await test_service.get_test_session(request.test_session_id)
        if not test_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy phiên làm bài với ID: {request.test_session_id}",
            )

        # 2. Kiểm tra quyền truy cập - chỉ user sở hữu test session mới được đánh giá
        if test_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập phiên làm bài này",
            )

        # 3. Kiểm tra test session đã hoàn thành chưa
        if test_session.status != "completed" or not test_session.is_submitted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiên làm bài chưa hoàn thành. Vui lòng hoàn thành bài kiểm tra trước khi yêu cầu đánh giá.",
            )

        # 4. Kiểm tra đã có điểm số chưa
        if test_session.score is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bài kiểm tra chưa được chấm điểm. Vui lòng đợi hệ thống xử lý.",
            )

        logger.info(
            f"Bắt đầu đánh giá trình độ cho user {current_user.id}, test session {request.test_session_id}"
        )

        # 5. Gọi AssessmentAgent để đánh giá
        assessment_result = await assessment_agent.act(
            test_session_id=request.test_session_id,
            user_id=current_user.id,
        )

        logger.info(f"Hoàn thành đánh giá trình độ cho user {current_user.id}")

        # 6. Convert result từ agent sang response schema
        response_data = {
            "test_session_id": assessment_result.test_session_id,
            "course_id": assessment_result.course_id,
            "overall_score": assessment_result.overall_score,
            "overall_level": assessment_result.overall_level,
            "topic_assessments": [
                {
                    "topic_id": ta.topic_id,
                    "topic_name": ta.topic_name,
                    "score_percentage": ta.score_percentage,
                    "level": ta.level,
                    "strengths": ta.strengths,
                    "weaknesses": ta.weaknesses,
                    "recommendations": ta.recommendations,
                }
                for ta in assessment_result.topic_assessments
            ],
            "learning_path": [
                {
                    "topic_id": lp.topic_id,
                    "topic_name": lp.topic_name,
                    "order": lp.order,
                    "priority": lp.priority,
                    "estimated_hours": lp.estimated_hours,
                    "reason": lp.reason,
                    "suggested_difficulty": lp.suggested_difficulty,
                }
                for lp in assessment_result.learning_path
            ],
            "general_feedback": assessment_result.general_feedback,
            "study_recommendations": assessment_result.study_recommendations,
            "next_steps": assessment_result.next_steps,
        }

        return AssessmentResultResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle validation errors from agent
        logger.error(f"Validation error in assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi trong quá trình đánh giá. Vui lòng thử lại sau.",
        )


@router.get(
    "/test-session/{test_session_id}/can-assess",
    summary="Kiểm tra xem có thể đánh giá test session không",
    description="""
    Endpoint để kiểm tra xem một test session có đủ điều kiện để đánh giá hay không.
    
    **Điều kiện cần thiết**:
    - Test session phải tồn tại
    - User phải có quyền truy cập  
    - Test session đã hoàn thành
    - Đã có điểm số
    """,
)
async def can_assess_test_session(
    test_session_id: str,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service),
) -> Dict[str, Any]:
    """
    Kiểm tra xem test session có thể được đánh giá không

    Args:
        test_session_id: ID của test session cần kiểm tra
        current_user: Thông tin người dùng hiện tại
        test_service: Service để xử lý logic liên quan đến test

    Returns:
        Dict chứa thông tin về khả năng đánh giá và lý do (nếu không thể)
    """
    try:
        # Kiểm tra test session có tồn tại không
        test_session = await test_service.get_test_session(test_session_id)
        if not test_session:
            return {
                "can_assess": False,
                "reason": "Không tìm thấy phiên làm bài",
                "test_session": None,
            }

        # Kiểm tra quyền truy cập
        if test_session.user_id != current_user.id:
            return {
                "can_assess": False,
                "reason": "Không có quyền truy cập phiên làm bài này",
                "test_session": None,
            }

        # Kiểm tra trạng thái hoàn thành
        if test_session.status != "completed" or not test_session.is_submitted:
            return {
                "can_assess": False,
                "reason": "Phiên làm bài chưa hoàn thành",
                "test_session": {
                    "id": test_session.id,
                    "status": test_session.status,
                    "is_submitted": test_session.is_submitted,
                },
            }

        # Kiểm tra có điểm số chưa
        if test_session.score is None:
            return {
                "can_assess": False,
                "reason": "Bài kiểm tra chưa được chấm điểm",
                "test_session": {
                    "id": test_session.id,
                    "status": test_session.status,
                    "is_submitted": test_session.is_submitted,
                    "score": test_session.score,
                },
            }

        # Tất cả điều kiện đều thỏa mãn
        return {
            "can_assess": True,
            "reason": "Phiên làm bài đủ điều kiện để đánh giá",
            "test_session": {
                "id": test_session.id,
                "status": test_session.status,
                "is_submitted": test_session.is_submitted,
                "score": test_session.score,
                "correct_answers": test_session.correct_answers,
            },
        }

    except Exception as e:
        logger.error(f"Error checking assessment eligibility: {e}")
        return {
            "can_assess": False,
            "reason": f"Lỗi hệ thống: {str(e)}",
            "test_session": None,
        }
