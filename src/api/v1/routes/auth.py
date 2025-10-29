from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.api.v1 import schemas as m
from src.api.v1.enums import Roles
from src.database.methods import UserMethods
from src.database.responses import SuccessResponse, FailedResponse
from src.utils.logger import logger
from src.api.v1 import responses
from pydantic import ValidationError
from src.api.v1.methods import security

router = APIRouter(prefix="/v1/auth", tags=['Authentication', 'Аутентификация'])


@router.post("/register", response_model=m.RegVisibleForm)
async def _(reg_form: m.RegForm):
    try:
        personal_info = {
            "username": reg_form.username,
            "password": security.hash_password(reg_form.password),
            "first_name": reg_form.first_name,
            "last_name": reg_form.last_name,
            "age": reg_form.age,
            "email": reg_form.email,
            "phone": reg_form.phone,
            "role": Roles.USER
        }
        model_pi = m.RegResponse(**personal_info)
        created_user = await UserMethods.register_user(model_pi)
        if isinstance(created_user, FailedResponse):
            details = created_user.detail
            status_code = created_user.status_code
            raise HTTPException(status_code=status_code, detail=responses.fail_response(status_code, details))
        data = m.RegVisibleForm(**created_user.data).model_dump()
        return JSONResponse(content=responses.success_response(200, data=data))
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(
            status_code=400,
            detail=responses.fail_response(400,
                                           "Данные введены в некорректной форме, исправьте ошибки и продолжайте регистрацию.")
        )


@router.post("/login")
async def _(tokens: dict = Depends(security.auth_user)):
    return {"access_token": tokens.get("access_token", None),
         "refresh_token": tokens.get("refresh_token", None)}


@router.get("/test")
async def _(username: dict = Depends(security.get_user)):
    return responses.success_response(status_code=200, data={"success": True, "user": username})
