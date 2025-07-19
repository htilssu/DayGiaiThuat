from fastapi import APIRouter, Depends, HTTPException, Body

from app.schemas.exercise_schema import CreateExerciseSchema, CodeSubmissionRequest, CodeSubmissionResponse
from app.services.exercise_service import ExerciseService, get_exercise_service

router = APIRouter(prefix="/exercise", tags=["Bài tập"])


@router.post(
    "/create",
    summary="Tạo bài tập mới",
    description="Tạo bài tập mới sử dụng AI agent dựa trên chủ đề và độ khó",
)
async def create_exercise(
    data: CreateExerciseSchema,
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    """
    Tạo bài tập mới sử dụng AI agent

    Args:
        data (CreateExerciseSchema): Dữ liệu để tạo bài tập
        exercise_service (ExerciseService): Service xử lý bài tập

    Returns:
        ExerciseSchema: Thông tin bài tập đã được tạo
    """
    try:
        exercise = await exercise_service.create_exercise(data)
        return exercise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo bài tập: {str(e)}")


@router.get(
    "/{exercise_id}",
    summary="Lấy thông tin bài tập",
    description="Lấy thông tin chi tiết của bài tập theo ID",
)
async def get_exercise(
    exercise_id: int,
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    """
    Lấy thông tin bài tập theo ID

    Args:
        exercise_id (int): ID của bài tập
        exercise_service (ExerciseService): Service xử lý bài tập

    Returns:
        ExerciseModel: Thông tin bài tập
    """
    exercise = await exercise_service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=404, detail=f"Không tìm thấy bài tập với ID {exercise_id}"
        )
    return exercise


@router.post(
    "/{exercise_id}/submit",
    summary="Nộp code bài tập và chấm điểm tự động",
    response_model=CodeSubmissionResponse,
)
async def submit_exercise_code(
    exercise_id: int,
    submission: CodeSubmissionRequest = Body(...),
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    """
    Nhận code, chạy với các test case và trả về kết quả từng test case.
    """
    return await exercise_service.evaluate_submission(exercise_id, submission)
