from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.v1.schemas import lesson_schema as lesson_m, user_schema as user_m
from src.api.v1.methods import security
from src.api.v1 import responses
from src.database.methods import LessonMethods, CourseMethods, ProgressMethods
from src.database.responses import FailedResponse
from src.api.v1.enums import LessonTypes as lt, MaterialTypes, ProgressTypes

router = APIRouter(prefix="/api/v1/lesson", tags=['Лекции/Уроки', 'Lessons'])


@router.post("/addLesson", description="Добавление урока")
async def _(data: lesson_m.LessonInput, user: user_m.UserResponse = Depends(security.get_user)):
    # Проверка на автора
    response = await CourseMethods.get_author(data.course_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(response.status_code,
                                         detail=response.detail)
        raise HTTPException(response.status_code, detail=detail)
    if user.username != response.data:
        detail = responses.fail_response(status_code=400,
                                         detail="Вы не являетесь автором этого курса")
        raise HTTPException(status_code=400, detail=detail)
    # Тип урока
    if data.question_lesson and data.answer_lesson:
        lesson_type = lt.PRACTICAL
    elif data.question_lesson or data.answer_lesson:
        detail = responses.fail_response(status_code=400,
                                         detail="Практическая лекция не может иметь вопрос без ответа и ответ без вопроса")
        raise HTTPException(status_code=400, detail=detail)
    else:
        lesson_type = lt.LECTURE
    # Проверка на указание попыток в практической лекции
    if lesson_type == lt.PRACTICAL and not data.attempts:
        detail = responses.fail_response(status_code=400,
                                         detail="Практическая лекция должна иметь попытки на выполнение")
        raise HTTPException(status_code=400, detail=detail)
    lesson = lesson_m.LessonAddModel(
        lesson_title=data.lesson_title,
        course_id=data.course_id,
        desc=data.desc,
        question_lesson=data.question_lesson,
        answer_lesson=data.answer_lesson,
        attempts=data.attempts,
        level=data.level,
        lesson_type=lesson_type
    )
    response = await LessonMethods.add_lesson(lesson)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)

    return responses.success_response(data={"message": "Урок успешно добавлен", "lesson": response.data})


@router.get("/getLessons", description="Получить все уроки из курса")
async def _(course_id: int = Query(..., description="Айди курса"),
            user: user_m.UserResponse = Depends(security.get_user)):
    result = await LessonMethods.get_lessons_in_course(course_id=course_id)
    if isinstance(result, FailedResponse):
        detail = responses.fail_response(status_code=result.status_code, detail=result.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    return responses.success_response(data=result.data)


@router.post("/sign", description="Подписаться на урок")
async def _(data: lesson_m.SignLesson, user: user_m.UserResponse = Depends(security.get_user)):
    response = await LessonMethods.get_lesson(data.lesson_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    attempts = vars(response.data).get("attempts")
    material = user_m.UserAddProgress(
        user_id=user.user_id,
        material_id=data.lesson_id,
        material_type=MaterialTypes.LECTURE,
        status=ProgressTypes.PROGRESS,
        attempts=attempts

    )
    result = await ProgressMethods.start_material(material)
    if isinstance(result, FailedResponse):
        detail = responses.fail_response(status_code=result.status_code, detail=result.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    return responses.success_response(data=result.data)


@router.post("/answerLesson", description="Завершить практический урок. (потратить попытку на ответ)")
async def _(data: lesson_m.AnswerLesson, user: user_m.UserResponse = Depends(security.get_user)):
    # Проверка на то, выполнено ли задание
    response = await ProgressMethods.get_status(user.user_id, data.lesson_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    if response.data == ProgressTypes.COMPLETED:
        detail = responses.fail_response(status_code=400, detail="Урок уже завершен")
        raise HTTPException(status_code=400, detail=detail)
    # Сверка ответа с правильным
    result = await LessonMethods.check_answer_lesson(data)
    if isinstance(result, FailedResponse):
        detail = responses.fail_response(status_code=result.status_code, detail=result.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    right = True if result.data else False
    if not right:
        # Отнятие попыток
        response = await ProgressMethods.update_attempts(user.user_id, data.lesson_id, 1)
        if isinstance(response, FailedResponse):
            detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
            raise HTTPException(status_code=result.status_code, detail=detail)
        model = response.data
        # Добавление в список ответов
        response = await ProgressMethods.update_user_answers(user.user_id, data.lesson_id, data.answer)
        # print("RESPONSE", response)
        if isinstance(response, FailedResponse):
            detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
            raise HTTPException(status_code=result.status_code, detail=detail)
        # print("DATA", response.data)
        model = model.model_copy(update={"user_answers": response.data, "status": ProgressTypes.PROGRESS}).model_dump()
        return responses.success_response(data={"right": right, 'message': model})
    # Изменение статуса выполнения задания
    response = await ProgressMethods.update_status(user.user_id, data.lesson_id, ProgressTypes.COMPLETED)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    # Изменение числа участников, которые выполнили урок
    response = await LessonMethods.add_success_lesson_people(data.lesson_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    return responses.success_response(data="Урок успешно выполнен!")


@router.post("/completeLesson", description="Завершить лекционный урок")
async def _(body: user_m.BasicProgressModel, user: user_m.UserResponse = Depends(security.get_user)):
    # Отметка лекционного урока как пройденного
    result = await ProgressMethods.complete_lesson(user.user_id, body.material_id)
    if isinstance(result, FailedResponse):
        detail = responses.fail_response(status_code=result.status_code, detail=result.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    # Изменение числа участников, которые выполнили урок
    response = await LessonMethods.add_success_lesson_people(body.material_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    return responses.success_response(data=result.data)

# @router.post("/completeLesson")
# async def _(progress_data: user_m.UserAddProgress, user: user_m.UserResponse = Depends(security.get_user)):
# response = await LessonMethods.add_lesson(lesson)
# if isinstance(response, FailedResponse):
#     raise HTTPException(status_code=response.status_code, detail=response.detail)
#
# return responses.success_response(data={"message": "Урок успешно добавлен", "lesson": response.data})


# @router.get("/getCourse")
# async def _(name: str = Query(default=None), id_: str = Query(default=None)):
#     search = course_m.SearchCourse(course_name=name, course_id=id_)
#     response = await CourseMethods.get_courses(course_search=search)
#     if isinstance(response, FailedResponse):
#         raise HTTPException(status_code=response.status_code, detail=response.detail)
#     return responses.success_response(data=response.data)
