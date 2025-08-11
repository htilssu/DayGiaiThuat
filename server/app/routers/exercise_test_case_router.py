from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.exercise_test_case_schema import (
    ExerciseTestCaseCreate,
    ExerciseTestCaseResponse,
    ExerciseTestCaseUpdate,
)
from app.services.exercise_test_case_service import (
    ExerciseTestCaseService,
    get_exercise_test_case_service,
)

router = APIRouter(prefix="/exercise/{exercise_id}/test-cases", tags=["Bài tập"])


@router.get("/", response_model=list[ExerciseTestCaseResponse])
async def list_test_cases(
    exercise_id: int,
    service: ExerciseTestCaseService = Depends(get_exercise_test_case_service),
):
    return await service.list_by_exercise(exercise_id)


@router.post("/", response_model=ExerciseTestCaseResponse)
async def create_test_case(
    exercise_id: int,
    body: ExerciseTestCaseCreate,
    service: ExerciseTestCaseService = Depends(get_exercise_test_case_service),
):
    if body.exercise_id != exercise_id:
        raise HTTPException(status_code=400, detail="exercise_id không khớp")
    return await service.create(body)


@router.get("/{test_case_id}", response_model=ExerciseTestCaseResponse)
async def get_test_case(
    exercise_id: int,  # noqa: F401 - present for path consistency
    test_case_id: int,
    service: ExerciseTestCaseService = Depends(get_exercise_test_case_service),
):
    return await service.get(test_case_id)


@router.put("/{test_case_id}", response_model=ExerciseTestCaseResponse)
async def update_test_case(
    exercise_id: int,  # noqa: F401 - present for path consistency
    test_case_id: int,
    body: ExerciseTestCaseUpdate,
    service: ExerciseTestCaseService = Depends(get_exercise_test_case_service),
):
    return await service.update(test_case_id, body)


@router.delete("/{test_case_id}")
async def delete_test_case(
    exercise_id: int,  # noqa: F401 - present for path consistency
    test_case_id: int,
    service: ExerciseTestCaseService = Depends(get_exercise_test_case_service),
):
    await service.delete(test_case_id)
    return {"ok": True}
