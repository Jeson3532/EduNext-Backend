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


