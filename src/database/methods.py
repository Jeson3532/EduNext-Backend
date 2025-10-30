from src.database.model import session_maker
from src.database.model import Users, Course, Lesson, UserProgress
from sqlalchemy import select, exists
from src.utils.logger import logger
from src.api.v1.schemas import auth_schema as auth_m
from src.api.v1.schemas import course_schema as course_m
from sqlalchemy.exc import IntegrityError, ProgrammingError
from src.database.responses import SuccessResponse, FailedResponse


class UserMethods:
    @classmethod
    async def register_user(cls, personal_info: auth_m.RegResponse):
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

    @classmethod
    async def get_user_id(cls, username: str):
        async with session_maker() as session:
            try:
                query = select(Users.id).where(Users.username == str(username))
                user_id = await session.execute(query)
                scalar = user_id.scalar()
                if scalar:
                    return SuccessResponse(status_code=200, data=scalar)
                return FailedResponse(status_code=404, detail="Пользователя не существует")
            except ProgrammingError as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")


class CourseMethods:
    @classmethod
    async def add_course(cls, course: course_m.CourseAddModel):
        async with session_maker() as session:
            try:
                dumped_model = course.model_dump()
                new_course = Course(**dumped_model)
                session.add(new_course)
                await session.commit()
                return SuccessResponse(status_code=200, data=dumped_model)
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
