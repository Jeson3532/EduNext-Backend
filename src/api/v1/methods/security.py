import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Body
from src.database.responses import SuccessResponse, FailedResponse
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from src.database.methods import UserMethods
from src.api.v1.schemas import auth_schema as auth_m, user_schema as user_m
from .__init__ import env_path
from src.utils.logger import logger
from src.api.v1.examples import auth_examples

load_dotenv(dotenv_path=env_path)

pwd = CryptContext(schemes=['bcrypt'], deprecated="auto")
SECRET = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def generate_access_token(sub, user_id, expires_min=15):
    utc_exp = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_min)
    data = {"sub": sub, "exp": utc_exp.timestamp(), "user_id": user_id}
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)


def generate_refresh_token(sub, user_id, expires_hours=24):
    utc_exp = datetime.now(tz=timezone.utc) + timedelta(hours=expires_hours)
    data = {"sub": sub, "exp": utc_exp.timestamp(), "user_id": user_id}
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)


def hash_password(password: str):
    return pwd.hash(password)


def verify_password(password: str, hash_pass: str):
    return pwd.verify(password, hash_pass)


async def auth_user(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username
    password = form.password

    result = await UserMethods.get_hash_password(username=username)
    if isinstance(result, FailedResponse):
        raise HTTPException(status_code=result.status_code, detail=result.detail)
    if not verify_password(password, result.data):
        raise HTTPException(status_code=401, detail="Введены неверные данные")
    response = await UserMethods.get_user_id(username=username)
    if isinstance(response, FailedResponse):
        raise HTTPException(status_code=response.status_code, detail=response.detail)
    return {
        'access_token': generate_access_token(sub=username, user_id=response.data),
        'refresh_token': generate_refresh_token(sub=username, user_id=response.data)
    }


async def refresh_token(token: auth_m.RefreshToken = Body(..., example=auth_examples.REFRESH_TOKEN_FORM)):
    try:
        payload = jwt.decode(token.refresh_token, SECRET, ALGORITHM)
        user: str = payload.get("sub")
        if not user:
            raise HTTPException(status_code=401, detail="Неверный токен доступа")
        response = await UserMethods.get_user_id(username=user)
        if isinstance(response, FailedResponse):
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        access_token = generate_access_token(sub=user, user_id=response.data)
        return {"access_token": access_token}
    except JWTError:
        raise HTTPException(status_code=400, detail="Невалидный токен")


async def get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, ALGORITHM)

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=404, detail="Пользователя не существует")
        response = await UserMethods.get_user_id(username=username)
        if isinstance(response, FailedResponse):
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        data = {
            "username": username,
            "user_id": response.data
        }
        return user_m.UserResponse(**data)
    except ExpiredSignatureError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Токен более недействителен")
    except JWTError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Невалидный токен")
