from src.database.model import session_maker
from src.database.model import Users, Course, Lesson, UserProgress, AiTasks
from sqlalchemy import select, exists, cast, String, update
from src.utils.logger import logger
from src.api.v1.schemas import auth_schema as auth_m
from src.api.v1.schemas import course_schema as course_m
from src.api.v1.schemas import user_schema as user_m
from src.api.v1.schemas import lesson_schema as lesson_m
from src.api.v1.schemas import tasks_schema as task_m
from sqlalchemy.exc import IntegrityError, ProgrammingError
from src.database.responses import SuccessResponse, FailedResponse
from src.api.v1.enums import MaterialTypes, ProgressTypes, LessonTypes
from datetime import datetime
from copy import deepcopy


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
                new_dumped_model = lesson.model_copy(update={"pos": response.data}).model_dump(exclude_none=True)
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

    @classmethod
    async def get_lessons_in_course(cls, course_id):
        async with session_maker() as session:
            try:
                query = select(Lesson).where(Lesson.course_id == course_id)

                result = await session.execute(query)
                lessons = result.scalars().all()

                if not lessons:
                    return FailedResponse(status_code=404,
                                          detail=f'В курсе нет лекций, либо его попросту не существует')
                return SuccessResponse(status_code=200, data=lessons)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def check_answer_lesson(cls, body: lesson_m.AnswerLesson):
        async with session_maker() as session:
            try:
                lesson_id = body.lesson_id
                user_answer = body.answer

                response = await cls.get_answer_in_lesson(lesson_id)
                if isinstance(response, FailedResponse):
                    return FailedResponse(status_code=response.status_code, detail=response.detail)
                if user_answer != response.data:
                    return SuccessResponse(status_code=200, data=False)
                return SuccessResponse(status_code=200, data=True)


            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def add_success_lesson_people(cls, lesson_id):
        async with session_maker() as session:
            try:
                query = select(Lesson).where(Lesson.id == lesson_id)
                state = await session.execute(query)
                lesson = state.scalar_one_or_none()
                if isinstance(lesson, FailedResponse):
                    return FailedResponse(status_code=404, detail=f"Урока с айди {lesson_id} не существует")
                lesson.lesson_num_success_peoples = lesson.lesson_num_success_peoples + 1
                await session.commit()
                return SuccessResponse(status_code=200, data=True)


            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @staticmethod
    async def get_answer_in_lesson(lesson_id):
        async with session_maker() as session:
            try:
                query = select(Lesson.answer_lesson).where(Lesson.id == lesson_id)
                state = await session.execute(query)
                answer = state.scalar()
                if not answer:
                    return FailedResponse(status_code=404,
                                          detail=f'У лекционного урока нет вопроса')
                return SuccessResponse(status_code=200, data=answer)
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
                dumped_model = progress.model_dump(exclude_none=True)
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
                    if isinstance(response, SuccessResponse):
                        return FailedResponse(status_code=400, detail=f'Прогресс уже начат')
                if material_type == MaterialTypes.LECTURE:
                    # Проверка наличия урока
                    response = await LessonMethods.get_lesson(lesson_id=material_id)
                    if isinstance(response, FailedResponse):
                        return FailedResponse(status_code=404, detail=f'Материала не существует')
                    # Проверка на дубликат прогресса
                    response = await cls.get_progress(material_id=material_id, user_id=user_id,
                                                      material_type=MaterialTypes.LECTURE)
                    if isinstance(response, SuccessResponse):
                        return FailedResponse(status_code=400, detail=f'Прогресс уже начат')
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
                if not progress:
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

    @classmethod
    async def get_status(cls, user_id, material_id):
        async with session_maker() as session:
            try:
                query = select(UserProgress.status).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id)
                result = await session.execute(query)
                progress_status = result.scalar()
                if not progress_status:
                    return FailedResponse(status_code=404, detail="Прогресс не начат")
                return SuccessResponse(status_code=200, data=progress_status)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def complete_lesson(cls, user_id, material_id):
        async with session_maker() as session:
            try:
                # Проверка типа лекции
                query = select(Lesson.lesson_type).where(
                    Lesson.id == material_id)
                state = await session.execute(query)
                lesson_type = state.scalar_one_or_none()
                if not lesson_type:
                    return FailedResponse(status_code=404,
                                          detail=f"Лекции с айди {material_id} не существует, либо Вы не записаны на урок")
                if lesson_type != LessonTypes.LECTURE:
                    return FailedResponse(status_code=400,
                                          detail=f"Данным методом можно завешить только лекционный урок")
                # Остальные условия
                query = select(UserProgress).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id)
                state = await session.execute(query)

                progress = state.scalar_one_or_none()
                if not progress:
                    return FailedResponse(status_code=404,
                                          detail="Вы не записаны на этот урок, либо этого урока попросту не существует")
                if progress.material_type != MaterialTypes.LECTURE:
                    return FailedResponse(status_code=400, detail="Материал не является лекцией")
                if progress.status != ProgressTypes.PROGRESS:
                    return FailedResponse(status_code=400, detail="Урок уже завершен")
                progress.status = ProgressTypes.COMPLETED
                copy_progress = user_m.UserProgressResponse(**vars(progress)).model_dump(exclude_none=True)
                await session.commit()
                return SuccessResponse(status_code=200, data=copy_progress)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @staticmethod
    async def get_user_attempts(user_id, material_id):
        async with session_maker() as session:
            try:
                query = select(UserProgress.attempts).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id)
                result = await session.execute(query)
                attempts = result.scalar()
                if attempts is None:
                    return FailedResponse(status_code=400,
                                          detail="У данного материала не предусмотрены попытки на ответ, либо вы не подписаны на урок")
                return SuccessResponse(status_code=200, data=attempts)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def update_attempts(cls, user_id, material_id, bias):
        async with session_maker() as session:
            try:
                result = await cls.get_user_attempts(user_id, material_id)
                if isinstance(result, FailedResponse):
                    return FailedResponse(status_code=result.status_code, detail=result.detail)
                old_attempts = deepcopy(result.data)
                print("OLD", old_attempts)
                if not old_attempts:
                    return FailedResponse(status_code=403, detail="Количество попыток превысило лимит")
                new_attempts = old_attempts - bias
                query = update(UserProgress).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id).values(attempts=new_attempts)
                await session.execute(query)
                await session.commit()
                model = user_m.UserUpdateProgress(
                    attempts=new_attempts,
                    user_id=user_id,
                    material_id=material_id
                )
                return SuccessResponse(status_code=200, data=model)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def update_status(cls, user_id, material_id, status):
        async with session_maker() as session:
            try:
                query = update(UserProgress).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id).values(status=status)
                await session.execute(query)
                await session.commit()
                model = user_m.UserUpdateProgress(
                    status=status,
                    user_id=user_id,
                    material_id=material_id
                )
                return SuccessResponse(status_code=200, data=model)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def update_user_answers(cls, user_id, material_id, new_answer):
        async with session_maker() as session:
            try:
                query = select(UserProgress).where(UserProgress.user_id == user_id).where(
                    UserProgress.material_id == material_id)
                state = await session.execute(query)
                user_progress = state.scalar_one_or_none()
                if not user_progress:
                    return FailedResponse(status_code=404, detail="Прогресс по данному материалу не начат")

                user_progress.user_answers = (user_progress.user_answers or []) + [new_answer]
                answers = deepcopy(user_progress.user_answers)
                await session.commit()
                return SuccessResponse(status_code=200, data=answers)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")


class AiTaskMethods:
    @classmethod
    async def add_task(cls, data: task_m.AddTaskModel):
        async with session_maker() as session:
            try:
                dumped_model = data.model_dump()
                new_task = AiTasks(**dumped_model)
                session.add(new_task)
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
    async def get_task(cls, task_id, user_id):
        async with session_maker() as session:
            try:
                query = select(AiTasks).where(AiTasks.id == task_id).where(AiTasks.user_id == user_id)
                state = await session.execute(query)
                task = state.scalar_one_or_none()
                if not task:
                    return FailedResponse(status_code=404, detail="У Вас нет задач от искусственного интеллекта с указанным айди")
                return SuccessResponse(status_code=200, data=task)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def complete_task(cls, task_id):
        async with session_maker() as session:
            try:
                query = select(AiTasks).where(AiTasks.id == task_id)
                state = await session.execute(query)
                task = state.scalar_one_or_none()
                if not task:
                    return FailedResponse(status_code=404,
                                          detail="Указанной задачи не существует")
                task.status = ProgressTypes.COMPLETED
                completed_task = deepcopy(task)
                await session.commit()
                return SuccessResponse(status_code=200, data={"status": "Успешно!", "body": completed_task})
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

    @classmethod
    async def get_user_tasks(cls, user_id):
        async with session_maker() as session:
            try:
                query = select(AiTasks.id, AiTasks.task, AiTasks.status).where(AiTasks.user_id == user_id)
                state = await session.execute(query)
                tasks = state.mappings().all()
                if not tasks:
                    return FailedResponse(status_code=404,
                                          detail="У пользователя нет задач от искусственного интеллекта")
                return SuccessResponse(status_code=200, data=tasks)
            except ProgrammingError as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Ошибка при получении данных")
            except Exception as e:
                logger.error(e)
                await session.rollback()
                return FailedResponse(status_code=500, detail="Произошла непредвиденная ошибка")

# import asyncio
# a = ProgressMethods()
# res = asyncio.run(a.update_user_answers(1, 5, "Jopa"))
# print(vars(res))
