from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.api.v1.schemas import auth_schema as auth_m, user_schema as user_m
from src.api.v1.enums import Roles
from src.database.methods import UserMethods
from src.database.responses import SuccessResponse, FailedResponse
from src.utils.logger import logger
from src.api.v1 import responses
from pydantic import ValidationError
from src.api.v1.methods import security
from src.api.v1.examples import auth_examples

router = APIRouter(prefix="/api/v1/auth", tags=['Authentication', 'Аутентификация'])


@router.post("/register", response_model=auth_m.RegVisibleForm, description="Регистрация пользователя в системе")
async def _(reg_form: auth_m.RegForm = Body(..., example=auth_examples.REG_FORM_EXAMPLE)):
    try:
        personal_info = {
            "username": reg_form.username,
            "password": security.hash_password(reg_form.password),
            "first_name": reg_form.first_name,
            "last_name": reg_form.last_name,
            "age": reg_form.age,
            "email": reg_form.email,
            "phone": reg_form.phone,
            "role": Roles.USER,
            # "success_in_a_row": 0
        }
        model_pi = auth_m.RegResponse(**personal_info)
        created_user = await UserMethods.register_user(model_pi)
        if isinstance(created_user, FailedResponse):
            details = created_user.detail
            status_code = created_user.status_code
            raise HTTPException(status_code=status_code, detail=responses.fail_response(status_code, details))
        data = auth_m.RegVisibleForm(**created_user.data).model_dump()
        return JSONResponse(content=responses.success_response(200, data=data))
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(
            status_code=400,
            detail=responses.fail_response(400,
                                           "Данные введены в некорректной форме, исправьте ошибки и продолжайте регистрацию.")
        )


@router.post("/login", description="Авторизация пользователя через OAuth 2.0")
async def _(tokens: dict = Depends(security.auth_user)):
    return {"access_token": tokens.get("access_token", None),
            "refresh_token": tokens.get("refresh_token", None)}


@router.post("/refresh", description="Энд-поинт для обновления истекшего токена доступа")
async def _(new_access_token: str = Depends(security.refresh_token)):
    return responses.success_response(status_code=200, data=new_access_token)


@router.get("/me", description="Тестовый энд-поинт для проверки авторизации в системе")
async def _(me: user_m.UserResponse = Depends(security.get_user)):
    return responses.success_response(status_code=200, data=f"Привет, {me.username}!")
