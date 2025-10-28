from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class RegForm(BaseModel):
    username: str = Field(..., description="Текстовый идентификатор пользователя (никнейм)")
    name: str = Field(..., description='Имя пользователя', min_length=2)
    age: int = Field(..., description='Возраст пользователя', ge=12)
    email: EmailStr = Field(..., description='Почта пользователя')
    phone: Optional[str] = Field(default=None, description='Контактный номер пользователя')


class RegResponse(RegForm):
    role: str = Field(..., description="Роль пользователя в системе")
