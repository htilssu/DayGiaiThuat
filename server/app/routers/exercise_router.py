from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy import select

from app.schemas.exercise_schema import (
    CreateExerciseSchema,
    CodeSubmissionRequest,
    CodeSubmissionResponse,
    ExerciseUpdate,
)
from app.services.exercise_service import (
    ExerciseService,
    get_exercise_service,
    evaluate_submission_with_judge0,
)
from app.database.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise_model import Exercise

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
    "",
    summary="Lấy danh sách bài tập",
)
async def list_exercises(
    page: int = Query(1, gt=0, description="Số trang"),
    limit: int = Query(12, gt=1, le=100, description="Số item mỗi trang"),
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    return await exercise_service.list_exercises(page=page, limit=limit)


@router.get(
    "/{exercise_id}",
    summary="Lấy thông tin bài tập",
    description="Lấy thông tin chi tiết của bài tập theo ID",
)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Lấy thông tin bài tập theo ID

    Args:
        exercise_id (int): ID của bài tập
        exercise_service (ExerciseService): Service xử lý bài tập

    Returns:
        ExerciseModel: Thông tin bài tập
    """
    exercise = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = exercise.scalar_one_or_none()
    if not exercise:
        raise HTTPException(
            status_code=404, detail=f"Không tìm thấy bài tập với ID {exercise_id}"
        )
    return exercise


@router.put(
    "/{exercise_id}",
    summary="Cập nhật bài tập",
)
async def update_exercise(
    exercise_id: int,
    data: ExerciseUpdate,
    exercise_service: ExerciseService = Depends(get_exercise_service),
):
    return await exercise_service.update_exercise(exercise_id, data)


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


@router.post(
    "/{exercise_id}/judge0-submit",
    summary="Nộp code bài tập và chấm điểm tự động qua Judge0",
    response_model=CodeSubmissionResponse,
)
async def submit_exercise_code_judge0(
    exercise_id: int,
    submission: CodeSubmissionRequest = Body(...),
):
    """
    Nhận code, chạy với các test case qua Judge0 và trả về kết quả từng test case.
    """
    return await evaluate_submission_with_judge0(exercise_id, submission)
