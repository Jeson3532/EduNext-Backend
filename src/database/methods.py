from src.database.model import session_maker
from src.database.model import Users
from sqlalchemy import select, exists
from src.utils.logger import logger
from src.api.v1 import models as m
from src.api.v1 import responses
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

class UserMethods:
        @classmethod
        async def register_user(cls, personal_info: m.RegResponse):
            async with session_maker() as session:
                try:
                    dumped_model = personal_info.model_dump()
                    new_user = Users(**dumped_model)
                    session.add(new_user)
                    await session.commit()
                    return dumped_model

                except IntegrityError as e:
                    logger.error(e)
                    return {"detail": "Пользователь уже существует."}
                except Exception as e:
                    logger.error(e)
