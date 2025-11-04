from pydantic import BaseModel, Field
from src.api.v1.examples import auth_examples
from typing import Optional


class UserResponse(BaseModel):
    username: str
    user_id: int


class UserAddProgress(BaseModel):
    user_id: int = Field(..., description="Айди пользователя")
    material_type: str = Field(..., description="Тип прогресса (курс/лекция)")
    material_id: int = Field(..., description="Айди курса/лекции")
    status: str = Field(..., description="Статус выполнения материала (in progress/completed)")
    attempts: Optional[int] = Field(default=None, description="Количество попыток у пользователя")


class UserUpdateProgress(BaseModel):
    user_id: int = Field(..., description="Айди пользователя")
    material_id: int = Field(..., description="Айди курса/лекции")
    status: Optional[str] = Field(default=None, description="Статус выполнения материала (in progress/completed)")
    attempts: Optional[int] = Field(default=None, description="Количество попыток")
    user_answers: Optional[list[str]] = Field(default=None, description="Список ответов пользователя")


class UserProgressResponse(BaseModel):
    user_id: int = Field(..., description="Айди пользователя")
    material_id: int = Field(..., description="Айди курса/лекции")
    material_type: Optional[str] = Field(default=None, description="Тип прогресса (курс/лекция)")
    user_answers: Optional[list[str]] = Field(default=None, description="Список ответов пользователя")
    attempts: Optional[int] = Field(default=None, description="Количество попыток")
    status: Optional[str] = Field(default=None, description="Статус выполнения материала (in progress/completed)")


class BasicProgressModel(BaseModel):
    material_id: int
