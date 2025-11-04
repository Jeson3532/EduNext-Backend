from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LessonInput(BaseModel):
    lesson_title: str = Field(..., description='Название урока')
    course_id: int = Field(..., description='Айди курса, к которому относится урок')
    desc: str = Field(..., description="Описание урока", min_length=12, max_length=256)
    level: int = Field(..., description="Уровень сложности", ge=1, le=3)
    question_lesson: Optional[str] = Field(default=None, description='Вопрос урока, на который нужно дать ответ')
    answer_lesson: Optional[str] = Field(default=None, description='Ответ урока')
    attempts: Optional[int] = Field(default=None, description='Сколько попыток дается на ответ', le=100)


class LessonAddModel(LessonInput):
    lesson_type: str = Field(default=..., description='Тип урока')
    lesson_num_success_peoples: int = Field(default=0, description="Количество людей, прошедших урок")
    pos: int = Field(default=0, description="Позиция урока в курсе")


class SignLesson(BaseModel):
    lesson_id: int


class AnswerLesson(BaseModel):
    lesson_id: int
    answer: str

