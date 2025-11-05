from pydantic import BaseModel, Field
from src.api.v1.enums import ProgressTypes
from typing import Optional


class TaskQuestionLesson(BaseModel):
    question: str = Field(..., description="Вопрос студента")


class TaskAnswerLesson(BaseModel):
    answer: str = Field(..., description="Ответ студента")


class AddTaskModel(BaseModel):
    user_id: int
    task: str
    answer: str
    status: str = Field(default=ProgressTypes.PROGRESS)
