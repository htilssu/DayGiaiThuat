"""
Router cho việc generate test
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.test_generation_service import (
    TestGenerationService,
    get_test_generation_service,
)
from app.utils.utils import get_current_user
from app.schemas.user_profile_schema import UserExcludeSecret

router = APIRouter(prefix="/test-generation", tags=["Test Generation"])


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    """
    Dependency để kiểm tra quyền admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tính năng này",
        )
    return current_user


@router.post(
    "/{course_id}/generate",
    summary="Tạo bài kiểm tra đầu vào bất đồng bộ (Async)",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Yêu cầu tạo test đã được tiếp nhận"},
        400: {"description": "Dữ liệu không hợp lệ"},
        403: {"description": "Không có quyền truy cập"},
        500: {"description": "Internal server error"},
    },
)
async def generate_test_async(
    course_id: int,
    test_generation_service: TestGenerationService = Depends(
        get_test_generation_service
    ),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Tạo bài kiểm tra đầu vào bất đồng bộ

    Tạo test trong background, trả về ngay lập tức
    """
    await test_generation_service.generate_input_test_async(course_id)
    return {"message": "Yêu cầu tạo test đã được tiếp nhận"}


@router.get(
    "/{course_id}/status",
    summary="Lấy trạng thái tạo test",
    responses={
        200: {"description": "Trạng thái tạo test"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
def get_test_generation_status(
    course_id: int,
    test_generation_service: TestGenerationService = Depends(
        get_test_generation_service
    ),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy trạng thái tạo test của khóa học
    """
    status = test_generation_service.get_test_generation_status(course_id)
    return {"course_id": course_id, "status": status}


@router.get(
    "/{course_id}/tests",
    summary="Lấy danh sách test của khóa học",
    responses={
        200: {"description": "Danh sách test"},
        404: {"description": "Không tìm thấy khóa học"},
    },
)
def get_course_tests(
    course_id: int,
    test_generation_service: TestGenerationService = Depends(
        get_test_generation_service
    ),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Lấy danh sách test của khóa học
    """
    tests = test_generation_service.get_course_tests(course_id)
    return tests


@router.delete(
    "/test/{test_id}",
    summary="Xóa test",
    responses={
        200: {"description": "Test đã được xóa"},
        404: {"description": "Không tìm thấy test"},
        500: {"description": "Lỗi khi xóa test"},
    },
)
def delete_test(
    test_id: int,
    test_generation_service: TestGenerationService = Depends(
        get_test_generation_service
    ),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Xóa test theo ID
    """
    success = test_generation_service.delete_test(test_id)
    if success:
        return {"message": "Test đã được xóa thành công"}
    else:
        return {"message": "Có lỗi khi xóa test"}
