"""
Router để quản lý đánh giá điểm yếu và mạnh của người dùng
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.services.user_assessment_service import (
    UserAssessmentService,
    get_user_assessment_service,
)
from app.schemas.user_assessment_schema import (
    UserAssessmentResponse,
    AssessmentAnalysisRequest,
    WeaknessAnalysisResult,
    StrengthAnalysisResult,
)
from app.utils.utils import get_current_user
from app.schemas.user_profile_schema import UserExcludeSecret

router = APIRouter(prefix="/assessments", tags=["Đánh giá người dùng"])


@router.get(
    "/test-session/{test_session_id}", response_model=Optional[UserAssessmentResponse]
)
async def get_assessment_by_test_session(
    test_session_id: str,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy kết quả đánh giá theo test session ID
    """
    assessment = await assessment_service.get_assessment_by_test_session(
        test_session_id
    )

    if assessment and assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem đánh giá của người dùng khác",
        )

    return assessment


@router.get("/my-assessments", response_model=List[UserAssessmentResponse])
async def get_my_assessments(
    limit: int = 10,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy danh sách đánh giá của người dùng hiện tại
    """
    assessments = await assessment_service.get_user_assessments(
        user_id=current_user.id, limit=limit
    )
    return assessments


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def trigger_assessment_analysis(
    analysis_request: AssessmentAnalysisRequest,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Kích hoạt phân tích đánh giá cho một test session (chạy trong background)
    """
    # Kiểm tra quyền: chỉ được phân tích cho chính mình
    if analysis_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ được phân tích cho chính mình",
        )

    # Bắt đầu phân tích trong background
    await assessment_service.analyze_user_weaknesses_background(analysis_request)

    return {
        "message": "Đã bắt đầu phân tích điểm yếu trong background",
        "test_session_id": analysis_request.test_session_id,
    }


@router.get("/weaknesses/{test_session_id}")
async def get_weakness_analysis(
    test_session_id: str,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy phân tích điểm yếu chi tiết theo test session
    """
    assessment = await assessment_service.get_assessment_by_test_session(
        test_session_id
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đánh giá cho test session này",
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem đánh giá của người dùng khác",
        )

    # Trích xuất thông tin điểm yếu
    weaknesses = assessment.weaknesses or {}
    weak_items = weaknesses.get("items", [])

    return {
        "test_session_id": test_session_id,
        "weaknesses": weak_items,
        "analysis_summary": assessment.analysis_summary,
        "recommendations": assessment.recommendations or {},
        "created_at": assessment.created_at,
    }


@router.get("/strengths/{test_session_id}")
async def get_strength_analysis(
    test_session_id: str,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy phân tích điểm mạnh chi tiết theo test session
    """
    assessment = await assessment_service.get_assessment_by_test_session(
        test_session_id
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đánh giá cho test session này",
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem đánh giá của người dùng khác",
        )

    # Trích xuất thông tin điểm mạnh
    strengths = assessment.strengths or {}
    strong_items = strengths.get("items", [])

    return {
        "test_session_id": test_session_id,
        "strengths": strong_items,
        "analysis_summary": assessment.analysis_summary,
        "learning_path": assessment.learning_path or {},
        "created_at": assessment.created_at,
    }


@router.get("/summary/{test_session_id}")
async def get_assessment_summary(
    test_session_id: str,
    assessment_service: UserAssessmentService = Depends(get_user_assessment_service),
    current_user: UserExcludeSecret = Depends(get_current_user),
):
    """
    Lấy tóm tắt đánh giá tổng quan theo test session
    """
    assessment = await assessment_service.get_assessment_by_test_session(
        test_session_id
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đánh giá cho test session này",
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem đánh giá của người dùng khác",
        )

    # Tạo summary từ assessment
    strengths = assessment.strengths or {}
    weaknesses = assessment.weaknesses or {}
    recommendations = assessment.recommendations or {}

    return {
        "test_session_id": test_session_id,
        "overall_score": assessment.overall_score,
        "proficiency_level": assessment.proficiency_level,
        "strengths_count": len(strengths.get("items", [])),
        "weaknesses_count": len(weaknesses.get("items", [])),
        "recommendations_count": len(recommendations.get("items", [])),
        "analysis_summary": assessment.analysis_summary,
        "skill_levels": assessment.skill_levels or {},
        "learning_path": assessment.learning_path or {},
        "created_at": assessment.created_at,
        "updated_at": assessment.updated_at,
    }
