from src.database.model import session_maker
from src.database.model import Users, Course, Lesson, UserProgress
from sqlalchemy import select, exists, cast, String, update
from src.utils.logger import logger
from src.api.v1.schemas import auth_schema as auth_m
from src.api.v1.schemas import course_schema as course_m
from src.api.v1.schemas import user_schema as user_m
from src.api.v1.schemas import lesson_schema as lesson_m
from sqlalchemy.exc import IntegrityError, ProgrammingError
from src.database.responses import SuccessResponse, FailedResponse
from src.api.v1.enums import MaterialTypes
from datetime import datetime


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
                await session.rollback()
                return FailedResponse(status_code=409, detail="Пользователь уже существует")
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
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
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
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
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
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
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @staticmethod
    async def update_num_lessons(session, course_id: int, count: int):
        try:
            query = update(Course).where(Course.id == course_id).values(num_lessons=count)
            await session.execute(query)
            return SuccessResponse(status_code=200, data="Количество лекций в курсе обновлено.")
        except ProgrammingError as e:
            logger.error(e)
            await session.rollback()
            return FailedResponse(status_code=500, detail="Ошибка при получении данных")
        except Exception as e:
            logger.error(e)
            await session.rollback()
            return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_courses(cls, course_search: course_m.SearchCourse):
        async with session_maker() as session:
            try:
                course_name = course_search.course_name
                course_id = course_search.course_id
                query = str()
                if not course_name and not course_id:
                    query = select(Course)
                elif course_name and course_id:
                    query = select(Course).where(cast(Course.course_title, String).contains(course_name)).where(
                        Course.id == course_id)
                elif course_name:
                    query = select(Course).where(cast(Course.course_title, String).contains(course_name))
                elif course_id:
                    query = select(Course).where(Course.id == course_id)

                result = await session.execute(query)
                courses = result.scalars().all()

                if not courses:
                    return FailedResponse(status_code=404, detail=f'По текущим фильтрам ничего не найдено')
                return SuccessResponse(status_code=200, data=courses)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_author(cls, course_id: int):
        async with session_maker() as session:
            try:
                query = select(Course.author).where(Course.id == course_id)

                result = await session.execute(query)
                author = result.scalar()

                if not author:
                    return FailedResponse(status_code=404,
                                          detail=f'Такого курса не существует, либо у курса нет автора')
                return SuccessResponse(status_code=200, data=author)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")


class LessonMethods:
    @classmethod
    async def add_lesson(cls, lesson: lesson_m.LessonAddModel):
        async with session_maker() as session:
            try:
                # Дамп модели в словарь
                dumped_model = lesson.model_dump()
                # Проверка существования курса
                course_id = dumped_model['course_id']
                course_search = course_m.SearchCourse(course_id=course_id)
                response = await CourseMethods.get_courses(course_search=course_search)

                if isinstance(response, FailedResponse):
                    return FailedResponse(status_code=404, detail=f'Курса с айди "{course_id}" не существует')
                # Получение количества уроков в курсе
                response = await cls.get_count_lessons_in_course(dumped_model['course_id'])
                if isinstance(response, FailedResponse):
                    return FailedResponse(status_code=500, detail="Ошибка при получении данных")
                # Добавление позиции новому уроку
                new_dumped_model = lesson.model_copy(update={"pos": response.data}).model_dump()
                new_lesson = Lesson(**new_dumped_model)
                # Изменение количества уроков в курсе на новое
                response = await CourseMethods.update_num_lessons(session, course_id, int(response.data) + 1)
                if isinstance(response, FailedResponse):
                    return FailedResponse(status_code=500, detail="Ошибка при попытке выполнить запрос")

                # Добавление урока в БД
                session.add(new_lesson)
                await session.commit()
                return SuccessResponse(status_code=200, data=new_dumped_model)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_lesson(cls, lesson_id):
        async with session_maker() as session:
            try:
                query = select(Lesson).where(Lesson.id == lesson_id)

                result = await session.execute(query)
                lesson = result.scalar()

                if not lesson:
                    return FailedResponse(status_code=404, detail=f'Урока с айди {lesson_id} не существует')
                return SuccessResponse(status_code=200, data=lesson)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @staticmethod
    async def get_count_lessons_in_course(course_id: int):
        async with session_maker() as session:
            try:
                query = select(Lesson).where(Lesson.course_id == course_id)
                result = await session.execute(query)
                num_lessons = len(result.scalars().all())
                return SuccessResponse(status_code=200, data=num_lessons)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")


class ProgressMethods:
    @classmethod
    async def start_material(cls, progress: user_m.UserAddProgress):
        async with session_maker() as session:
            try:
                dumped_model = progress.model_dump()
                material_type = dumped_model.get("material_type")
                material_id = dumped_model.get("material_id")
                user_id = dumped_model.get("user_id")
                if not material_type:
                    return FailedResponse(status_code=400, detail="Не указан тип материала")
                if material_type == MaterialTypes.COURSE:
                    # Проверка наличия курса
                    course_search = course_m.SearchCourse(course_id=material_id)
                    response = await CourseMethods.get_courses(course_search=course_search)
                    if isinstance(response, FailedResponse):
                        return FailedResponse(status_code=404, detail=f'Материала не существует')
                    # Проверка на дубликат прогресса
                    response = await cls.get_progress(material_id=material_id, user_id=user_id,
                                                      material_type=MaterialTypes.COURSE)
                    if isinstance(response, FailedResponse):
                        return FailedResponse(status_code=404, detail=f'Прогресс уже начат')
                if material_type == MaterialTypes.LECTURE:
                    # Проверка наличия урока
                    response = await LessonMethods.get_lesson(lesson_id=material_id)
                    if isinstance(response, FailedResponse):
                        return FailedResponse(status_code=404, detail=f'Материала не существует')
                    # Проверка на дубликат прогресса
                    response = await cls.get_progress(material_id=material_id, user_id=user_id,
                                                      material_type=MaterialTypes.LECTURE)
                    if isinstance(response, FailedResponse):
                        return FailedResponse(status_code=404, detail=f'Прогресс уже начат')
                progress_model = UserProgress(**dumped_model)
                session.add(progress_model)
                await session.commit()
                return SuccessResponse(status_code=200, data=dumped_model)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_progress(cls, user_id, material_id, material_type):
        async with session_maker() as session:
            try:
                query = select(UserProgress).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id).where(UserProgress.material_type == material_type)
                result = await session.execute(query)
                progress = result.scalar()
                if progress:
                    return FailedResponse(status_code=404, detail="Прогресс не начат")
                return SuccessResponse(status_code=200, data=progress)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

# import asyncio
# a = CourseMethods()
# res = asyncio.run(a.get_courses())
# print(vars(res))
