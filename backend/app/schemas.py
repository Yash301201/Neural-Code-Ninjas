from datetime import datetime, date, time
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, EmailStr, model_validator

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Login(Input):
    email: EmailStr
    password: str

class UserCreate(Input):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: Literal['ADMIN','HOD','FACULTY','STUDENT']
    department_id: int | None = None
    registration_number: str | None = None

class Question(Input):
    topic_id: int
    question_text: str = Field(min_length=1, max_length=12000)
    question_type: Literal['MCQ','TRUE_FALSE','SHORT_ANSWER','DESCRIPTIVE']
    difficulty: Literal['EASY','MEDIUM','HARD'] = 'MEDIUM'
    choice_options: list[str] = Field(default_factory=list, max_length=10)
    correct_answer: str | None = None
    explanation: str | None = None
    @model_validator(mode='after')
    def objective(self):
        if self.question_type in ('MCQ','TRUE_FALSE') and (not self.correct_answer or self.correct_answer not in self.choice_options):
            raise ValueError('Objective answer must be one of choice_options')
        if self.question_type == 'MCQ' and len(self.choice_options) < 2:
            raise ValueError('MCQ needs at least two options')
        return self

class Review(Input):
    review_status: Literal['APPROVED','REJECTED','PENDING_REVIEW']

class TestQuestion(Input):
    question_id: int
    marks: float = Field(gt=0, le=1000)

class TestCreate(Input):
    subject_id: int
    section_id: int
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    duration_minutes: int = Field(default=30, ge=1, le=300)
    start_at: datetime | None = None
    end_at: datetime | None = None
    max_attempts: int = Field(default=1, ge=1, le=10)
    questions: list[TestQuestion] = Field(min_length=1, max_length=100)
    @model_validator(mode='after')
    def valid(self):
        for d in (self.start_at, self.end_at):
            if d and d.tzinfo:
                raise ValueError('Use UTC datetimes without an offset')
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError('end_at must follow start_at')
        if len({q.question_id for q in self.questions}) != len(self.questions):
            raise ValueError('Duplicate questions')
        return self

class Answer(Input):
    question_id: int
    answer_text: str = Field(max_length=20000)
class Submit(Input):
    answers: list[Answer] = Field(max_length=100)
class Grade(Input):
    marks: float = Field(ge=0)
    feedback: str = Field(default='', max_length=10000)
class Assignment(Input):
    subject_id: int
    section_id: int
    title: str = Field(min_length=1, max_length=160)
    description: str = ''
    due_at: datetime
    max_marks: float = Field(default=100, gt=0, le=10000)
    @model_validator(mode='after')
    def utc(self):
        if self.due_at.tzinfo:
            raise ValueError('Use UTC datetime without offset')
        return self
class Submission(Input):
    answer_text: str = Field(min_length=1, max_length=30000)
class AttendanceItem(Input):
    student_id: int
    status: Literal['PRESENT','ABSENT','LATE','LEAVE']
class Attendance(Input):
    subject_id: int
    section_id: int
    topic_id: int | None = None
    session_date: date
    starts_at: time
    records: list[AttendanceItem] = Field(min_length=1, max_length=500)
class PlanRequest(Input):
    student_id: int
    subject_id: int
    days: int = Field(default=7, ge=1, le=30)
class PlanStatus(Input):
    status: Literal['PENDING','IN_PROGRESS','COMPLETED','SKIPPED']
class Doubt(Input):
    topic_id: int
    question: str = Field(min_length=1, max_length=3000)
    language: Literal['English','Telugu'] = 'English'
class Generate(Input):
    topic_id: int
    count: int = Field(default=3, ge=1, le=10)
    difficulty: Literal['EASY','MEDIUM','HARD'] = 'MEDIUM'
