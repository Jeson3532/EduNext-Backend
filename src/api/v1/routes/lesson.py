from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from src.api.v1.schemas import lesson_schema as lesson_m, user_schema as user_m, tasks_schema as task_m
from src.api.v1.methods import security
from src.api.v1 import responses
from src.database.methods import LessonMethods, CourseMethods, ProgressMethods, AiTaskMethods, UserMethods
from src.database.responses import FailedResponse
from src.api.v1.enums import LessonTypes as lt, MaterialTypes, ProgressTypes
from src.ai_agent.yandex_gpt import get_answer_ai, generate_task, compare_answers
from src.api.v1.examples import lesson_examples
import json
from src.badges.dispatcher import BadgeDispatcher
from src.badges.status import BadgeScanStatus

router = APIRouter(prefix="/api/v1/lesson", tags=['Лекции/Уроки', 'Lessons'])


@router.post("/addLesson", description="Добавление урока и прикрепление его к определенному курсу.\n"
                                       "Для создания лекционного урока, требуется убрать ключи question_lesson, answer_lesson, attempts.")
async def _(data: lesson_m.LessonInput = Body(..., example=lesson_examples.ADD_LESSON_EXAMPLE),
            user: user_m.UserResponse = Depends(security.get_user)):
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
        material=data.material,
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


@router.post("/sign", description="Подписаться на урок для начала прогресса в системе")
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
    dispatcher = BadgeDispatcher(user.user_id)
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
        # Обнуление решенных задач подряд
        response = await UserMethods.update_success_in_a_row(user_id=user.user_id, reset=True)
        if isinstance(response, FailedResponse):
            detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
            raise HTTPException(status_code=result.status_code, detail=detail)
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
    # Добавление задачи в ряд
    response = await UserMethods.update_success_in_a_row(user_id=user.user_id, bias=1)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    # Проверка выдачи достижений
    scan_result = await dispatcher.scan()
    state_message = "Урок успешно выполнен!"
    final_message = state_message + " У Вас новое достижение." if BadgeScanStatus.SUCCESS in scan_result.values() \
        else state_message
    return responses.success_response(data=final_message)


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


@router.post("/{lesson_id}/ask", tags=['AI-Tasks', 'ИИ-Задачи'], description="Задать вопрос по уроку AI-помощнику")
async def _(lesson_id: int = Path(..., description="Айди урока"), q_body: task_m.TaskQuestionLesson = Body(...),
            user: user_m.UserResponse = Depends(security.get_user)):
    response = await LessonMethods.get_lesson(lesson_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    data = response.data

    lesson_name = data.lesson_title
    lesson_desc = data.desc
    material = data.material
    ai_answer = get_answer_ai(lesson_name, lesson_desc, material, q_body.question)
    return responses.success_response(data=ai_answer)


@router.post("/{lesson_id}/generate-task", tags=['AI-Tasks', 'ИИ-Задачи'],
             description="Сгенерировать задачу по контексту урока")
async def _(lesson_id: int = Path(..., description="Айди урока"),
            user: user_m.UserResponse = Depends(security.get_user)):
    response = await LessonMethods.get_lesson(lesson_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    data = response.data
    # Данные о уроке
    lesson_name = data.lesson_title
    lesson_desc = data.desc
    # Генерация задачи и конвертация в json
    ai_task = generate_task(lesson_name, lesson_desc)
    json_ai_task = json.loads(ai_task)
    model = task_m.AddTaskModel(
        user_id=user.user_id,
        task=json_ai_task['task'],
        answer=json_ai_task['answer']
    )
    # Добавление таски в БД
    response = await AiTaskMethods.add_task(model)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    return responses.success_response(data=json_ai_task['task'])


@router.post("/{task_id}/answer-ai-task", tags=['AI-Tasks', 'ИИ-Задачи'], description="Ответить на задачу от ИИ")
async def _(task_id: int = Path(..., description="Айди задания, которое сгенерировала нейросеть"),
            answer: task_m.TaskAnswerLesson = Body(...),
            user: user_m.UserResponse = Depends(security.get_user)):
    # Получение таски
    response = await AiTaskMethods.get_task(task_id, user.user_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    # Проверка статуса выполнения задания
    data = response.data
    if data.status == ProgressTypes.COMPLETED:
        detail = responses.fail_response(status_code=400, detail="Задание уже завершено")
        raise HTTPException(status_code=400, detail=detail)
    # Проверка правильности ответа
    true_answer = data.answer
    ai_solution = compare_answers(answer, true_answer)
    if json.loads(ai_solution):
        # Пометка успешного выполнения задания в БД
        response = await AiTaskMethods.complete_task(task_id)
        if isinstance(response, FailedResponse):
            detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
            raise HTTPException(status_code=response.status_code, detail=detail)
        return responses.success_response(data=response.data)
    else:
        return responses.success_response(data="К сожалению, ответ неверный.")


@router.get("/get-ai-tasks", tags=['AI-Tasks', 'ИИ-Задачи'],
            description="Получить список задач, которые сгенерировала нейросеть лично для пользователя")
async def _(user: user_m.UserResponse = Depends(security.get_user)):
    # Получение тасок пользователя
    response = await AiTaskMethods.get_user_tasks(user.user_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)

    return responses.success_response(data=response.data)
