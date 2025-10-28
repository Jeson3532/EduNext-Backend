from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.api.v1 import models as m
from src.api.v1.enums import Roles
from src.database.methods import UserMethods
from src.utils.logger import logger
from src.api.v1 import responses
from pydantic import ValidationError

router = APIRouter(prefix="/v1/auth", tags=['Authentication', 'Аутентификация'])


@router.post("/register")
async def _(reg_form: m.RegForm):
    try:
        personal_info = {
            "username": reg_form.username,
            "name": reg_form.name,
            "age": reg_form.age,
            "email": reg_form.email,
            "phone": reg_form.phone,
            "role": Roles.USER
        }
        model_pi = m.RegResponse(**personal_info)
        created_user = await UserMethods.register_user(model_pi)
        if 'detail' in created_user.keys():
            details = created_user['detail']
            raise HTTPException(status_code=400, detail=responses.fail_response(400, details))
        return JSONResponse(content=responses.success_response(200, data=created_user))
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=responses.fail_response(400,
                                           "Данные введены в некорректной форме, исправьте ошибки и продолжайте регистрацию.")
        )
