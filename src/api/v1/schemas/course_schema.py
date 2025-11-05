from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CourseInput(BaseModel):
    course_title: str = Field(..., description='Название курса', min_length=5)
    desc: str = Field(..., description="Описание курса", min_length=12, max_length=256)
    course_categories: str = Field(..., description="Категории курса")


class CourseModel(BaseModel):
    id: int = Field(..., description='Идентификатор курса')
    course_title: str = Field(..., description='Название курса', min_length=5)
    author: str = Field(..., description="Автор курса")
    desc: str = Field(..., description="Описание курса", min_length=12, max_length=256)
    course_categories: str = Field(..., description="Категории курса")
    course_num_peoples: int = Field(default=0, description="Количество людей, записанных на курс")
    num_lessons: int = Field(default=0, description="Количество уроков в курсе")

    model_config = ConfigDict(from_attributes=True)


class CourseAddModel(CourseInput):
    num_lessons: int = Field(default=0, description="Количество уроков в курсе")
    author: str = Field(..., description="Автор курса")
    course_num_peoples: int = Field(default=0, description="Количество людей, записанных на курс")


class SearchCourse(BaseModel):
    course_name: Optional[str] = Field(default=None, description="Поиск по названию курса")
    course_id: Optional[int] = Field(default=None, description="Поиск по айди курса")


class UpdateNumLessons(BaseModel):
    num_lessons: int = Field(..., description="Новое количество уроков в курсе")


class SignCourse(BaseModel):
    course_id: int
