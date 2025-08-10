from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_db
from app.models.exercise_model import Exercise
from app.models.exercise_test_case_model import ExerciseTestCase
from app.schemas.exercise_test_case_schema import (
    ExerciseTestCaseCreate,
    ExerciseTestCaseResponse,
    ExerciseTestCaseUpdate,
)


class ExerciseTestCaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_exercise(self, exercise_id: int) -> Exercise:
        exercise = await self.db.get(Exercise, exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
        return exercise

    async def create(self, data: ExerciseTestCaseCreate) -> ExerciseTestCaseResponse:
        await self.ensure_exercise(data.exercise_id)
        test_case = ExerciseTestCase(
            exercise_id=data.exercise_id,
            input_data=data.input_data,
            output_data=data.output_data,
            explain=data.explain or "",
        )
        self.db.add(test_case)
        await self.db.commit()
        await self.db.refresh(test_case)
        return ExerciseTestCaseResponse.model_validate(test_case)

    async def list_by_exercise(self, exercise_id: int) -> list[ExerciseTestCaseResponse]:
        await self.ensure_exercise(exercise_id)
        result = await self.db.execute(
            select(ExerciseTestCase).where(ExerciseTestCase.exercise_id == exercise_id)
        )
        items = list(result.scalars().all())
        return [ExerciseTestCaseResponse.model_validate(i) for i in items]

    async def get(self, test_case_id: int) -> ExerciseTestCaseResponse:
        test_case = await self.db.get(ExerciseTestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="Không tìm thấy test case")
        return ExerciseTestCaseResponse.model_validate(test_case)

    async def update(self, test_case_id: int, data: ExerciseTestCaseUpdate) -> ExerciseTestCaseResponse:
        test_case = await self.db.get(ExerciseTestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="Không tìm thấy test case")
        if data.input_data is not None:
            test_case.input_data = data.input_data
        if data.output_data is not None:
            test_case.output_data = data.output_data
        if data.explain is not None:
            test_case.explain = data.explain
        await self.db.commit()
        await self.db.refresh(test_case)
        return ExerciseTestCaseResponse.model_validate(test_case)

    async def delete(self, test_case_id: int) -> None:
        test_case = await self.db.get(ExerciseTestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="Không tìm thấy test case")
        await self.db.delete(test_case)
        await self.db.commit()


def get_exercise_test_case_service(
    db: AsyncSession = Depends(get_async_db),
) -> ExerciseTestCaseService:
    return ExerciseTestCaseService(db)
