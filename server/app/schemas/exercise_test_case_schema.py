from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ExerciseTestCaseBase(BaseModel):
    input_data: str = Field(..., description="Dữ liệu đầu vào cho test case")
    output_data: str = Field(..., description="Kết quả mong đợi của test case")
    explain: Optional[str] = Field(None, description="Giải thích test case")


class ExerciseTestCaseCreate(ExerciseTestCaseBase):
    exercise_id: int = Field(..., description="ID bài tập")


class ExerciseTestCaseUpdate(BaseModel):
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    explain: Optional[str] = None


class ExerciseTestCaseResponse(ExerciseTestCaseBase):
    id: int
    exercise_id: int

    class Config:
        from_attributes = True
