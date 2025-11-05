from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional


class RegForm(BaseModel):
    username: str = Field(..., description="Текстовый идентификатор пользователя (никнейм)")
    password: str = Field(..., description="Хешированный пароль пользователя")
    first_name: str = Field(..., description='Имя пользователя', min_length=2)
    last_name: str = Field(..., description='Фамилия пользователя', min_length=2)
    age: int = Field(..., description='Возраст пользователя', ge=12)
    email: EmailStr = Field(..., description='Почта пользователя')
    phone: Optional[PhoneNumber] = Field(default=None, description='Контактный номер пользователя')


class RegResponse(RegForm):
    role: str = Field(..., description="Роль пользователя в системе")


class RegVisibleForm(BaseModel):
    username: str = Field(..., description="Текстовый идентификатор пользователя (никнейм)")
    first_name: str = Field(..., description='Имя пользователя', min_length=2)
    last_name: str = Field(..., description='Фамилия пользователя', min_length=2)
    age: int = Field(..., description='Возраст пользователя', ge=12)
    email: EmailStr = Field(..., description='Почта пользователя')
    phone: Optional[str] = Field(default=None, description='Контактный номер пользователя')


class RefreshToken(BaseModel):
    refresh_token: str
