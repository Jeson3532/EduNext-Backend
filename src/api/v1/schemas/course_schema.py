from pydantic import BaseModel, Field
from typing import Optional


class CourseResponse(BaseModel):
    course_title: str = Field(..., description='Название курса', min_length=5)
    desc: str = Field(..., description="Описание курса", min_length=12)
    course_categories: str = Field(..., description="Категории курса")


class CourseAddModel(CourseResponse):
    num_lessons: int = Field(default=0, description="Количество уроков в курсе")
    author: str = Field(..., description="Автор курса")
    course_num_peoples: int = Field(default=0, description="Количество людей, записанных на курс")

class SearchCourse(BaseModel):
    course_name: str = Field(default=None, description="Поиск по названию курса")
    course_id : Optional[str] = Field(default=None, description="Поиск по айди курса")

