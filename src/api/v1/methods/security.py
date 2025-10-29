import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from src.database.responses import SuccessResponse, FailedResponse
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from src.database.methods import UserMethods
from __init__ import env_path
from src.utils.logger import logger

load_dotenv(dotenv_path=env_path)

pwd = CryptContext(schemes=['bcrypt'], deprecated="auto")
SECRET = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def generate_access_token(sub, expires_min=15):
    utc_exp = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_min)
    data = {"sub": sub, "exp": utc_exp.timestamp()}
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)


def generate_refresh_token(sub, expires_hours=24):
    utc_exp = datetime.now(tz=timezone.utc) + timedelta(hours=expires_hours)
    data = {"sub": sub, "exp": utc_exp.timestamp()}
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)


def hash_password(password: str):
    return pwd.hash(password)


def verify_password(password: str, hash_pass: str):
    return pwd.verify(password, hash_pass)


async def auth_user(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username
    password = form.password

    result = await UserMethods.get_hash_password(username=username)
    print("RESULT:", result)
    if isinstance(result, FailedResponse):
        raise HTTPException(status_code=result.status_code, detail=result.detail)
    if not verify_password(password, result.data):
        raise HTTPException(status_code=401, detail="Введены неверные данные")
    return {
        'access_token': generate_access_token(sub=username),
        'refresh_token': generate_refresh_token(sub=username)
    }


def get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, ALGORITHM)

        username = payload.get("sub", None)
        if not username:
            raise HTTPException(status_code=404, detail="Пользователя не существует")
        return username
    except ExpiredSignatureError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Токен истек")
    except JWTError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Произошла ошибка при попытке обработать токен")
