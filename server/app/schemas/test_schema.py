from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field


class TestQuestionOption(BaseModel):
    id: str
    text: str


class TestQuestion(BaseModel):
    id: str
    title: str
    content: str
    type: str = Field(..., description="Loại câu hỏi: 'multiple_choice' hoặc 'problem'")
    options: Optional[List[TestQuestionOption]] = None
    code_template: Optional[str] = None


class TestBase(BaseModel):
    topic_id: Optional[int] = None
    course_id: Optional[int] = None
    duration_minutes: int = 60


class TestCreate(TestBase):
    questions: Dict[str, Any] = {}


class TestUpdate(BaseModel):
    duration_minutes: Optional[int] = None
    questions: Optional[Dict[str, Any]] = None


class TestInDB(TestBase):
    id: int
    questions: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class TestRead(TestInDB):
    pass


class TestSessionBase(BaseModel):
    user_id: int
    test_id: int


class TestSessionCreate(TestSessionBase):
    pass


class TestSessionUpdate(BaseModel):
    current_question_index: Optional[int] = None
    answers: Optional[Dict[str, Any]] = None
    time_remaining_seconds: Optional[int] = None
    last_activity: Optional[datetime] = None
    status: Optional[str] = None
    is_submitted: Optional[bool] = None


class TestSessionInDB(TestSessionBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    last_activity: datetime
    time_remaining_seconds: int
    status: str
    is_submitted: bool
    current_question_index: int
    answers: Dict[str, Any] = {}
    score: Optional[float] = None
    correct_answers: Optional[int] = None

    class Config:
        from_attributes = True


class TestSessionRead(TestSessionInDB):
    pass


class TestSessionResponse(TestSessionInDB):
    pass


class TestSessionWithTest(TestSessionRead):
    test: TestRead


class TestAnswerSubmit(BaseModel):
    question_id: str
    answer: Union[str, List[str], Dict[str, Any]]


class TestSubmission(BaseModel):
    answers: Dict[str, Any]


class QuestionFeedback(BaseModel):
    is_correct: bool
    feedback: Optional[str] = None


class TestResult(BaseModel):
    score: float
    total_questions: int
    correct_answers: int
    feedback: Dict[str, QuestionFeedback] = {}
