from src.database.model import session_maker
from src.database.model import Users
from sqlalchemy import select, exists
from src.utils.logger import logger
from src.api.v1 import schemas as m
from sqlalchemy.exc import IntegrityError, ProgrammingError
from src.database.responses import SuccessResponse, FailedResponse


class UserMethods:
    @classmethod
    async def register_user(cls, personal_info: m.RegResponse):
        async with session_maker() as session:
            try:
                dumped_model = personal_info.model_dump()
                new_user = Users(**dumped_model)
                session.add(new_user)
                await session.commit()
                return SuccessResponse(status_code=200, data=dumped_model)

            except IntegrityError as e:
                logger.error(e)
                return FailedResponse(status_code=409, detail="Пользователь уже существует")
            except ProgrammingError as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_hash_password(cls, username: str):
        async with session_maker() as session:
            try:
                query = select(Users.password).where(Users.username == str(username))
                password = await session.execute(query)
                scalar = password.scalar()
                if scalar:
                    return SuccessResponse(status_code=200, data=scalar)
                return FailedResponse(status_code=404, detail="Пользователя не существует")
            except ProgrammingError as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")
# import asyncio
# a = UserMethods()
# res = asyncio.run(a.get_hash_password(username='string'))
# print(res)
