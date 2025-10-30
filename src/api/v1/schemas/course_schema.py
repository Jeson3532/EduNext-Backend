from pydantic import BaseModel, Field


class CourseResponse(BaseModel):
    course_title: str = Field(..., description='Название курса', min_length=5)
    desc: str = Field(..., description="Описание курса", min_length=12)
    course_categories: str = Field(..., description="Категории курса")


class CourseAddModel(CourseResponse):
    num_lessons: int = Field(default=0, description="Количество уроков в курсе")
    author: str = Field(..., description="Автор курса")
    course_num_peoples: int = Field(default=0, description="Количество людей, записанных на курс")
