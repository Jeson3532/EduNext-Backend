from src.database.model import session_maker
from src.database.model import Users, Course, Lesson, UserProgress
from sqlalchemy import select, exists, cast, String
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

    @classmethod
    async def get_courses(cls):
        async with session_maker() as session:
            try:
                query = select(Course)
                result = await session.execute(query)
                courses = result.all()
                if not courses:
                    return FailedResponse(status_code=404, detail="Курсы не найдены")
                return SuccessResponse(status_code=200, data=courses)
            except ProgrammingError as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_courses_by_name(cls, course_search: course_m.SearchCourse):
        async with session_maker() as session:
            try:
                course_name = course_search.course_name
                if not course_name:
                    return FailedResponse(status_code=400, detail="Не передан параметр course_name при попытке поиска по названию.")
                query = select(Course).where(cast(Course.course_title, String).contains(course_name))
                result = await session.execute(query)
                courses = result.all()
                if not courses:
                    return FailedResponse(status_code=404, detail=f'Курсы с упоминанием "{course_name}" не найдены')
                return SuccessResponse(status_code=200, data=courses)
            except ProgrammingError as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_courses_by_id(cls, course_search: course_m.SearchCourse):
        async with session_maker() as session:
            try:
                course_id = course_search.course_id
                if not course_id:
                    return FailedResponse(status_code=400,
                                          detail="Не передан параметр course_id при попытке поиска по ID.")
                query = select(Course).where(Course.id == course_id)
                result = await session.execute(query)
                courses = result.all()
                if not courses:
                    return FailedResponse(status_code=404, detail=f'Курс с айди "{course_id}" не найден')
                return SuccessResponse(status_code=200, data=courses)
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
