from fastapi import APIRouter, Depends, HTTPException, Query, Body
from src.api.v1.schemas import course_schema as course_m, user_schema as user_m
from src.api.v1.methods import security, patch_allow_attr
from src.api.v1 import responses
from src.api.v1.enums import MaterialTypes, ProgressTypes
from src.database.methods import CourseMethods, ProgressMethods
from src.database.responses import FailedResponse
from pydantic import ValidationError
from src.api.v1.examples import course_examples

router = APIRouter(prefix="/api/v1/course", tags=['Курсы', 'Courses'])


@router.post("/addCourse", description="Добавление курса")
async def _(data: course_m.CourseInput = Body(..., example=course_examples.ADD_COURSE_EXAMPLE),
            user: user_m.UserResponse = Depends(security.get_user)):
    course = course_m.CourseAddModel(
        course_title=data.course_title,
        author=user.username,
        desc=data.desc,
        course_categories=data.course_categories,
    )
    response = await CourseMethods.add_course(course)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)

    return responses.success_response(data={"message": "Курс успешно создан", "course": course})


@router.get("/getCourse",
            description="Получение курса в системе. Фильтрация идёт по названию курса и его идентификатору")
async def _(name: str = Query(default=None, description="Название курса"),
            id_: str = Query(default=None, description="Айди курса"),
            user: user_m.UserResponse = Depends(security.get_user)):
    try:
        search = course_m.SearchCourse(course_name=name, course_id=id_)
        response = await CourseMethods.get_courses(course_search=search)
        if isinstance(response, FailedResponse):
            detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
            raise HTTPException(status_code=response.status_code, detail=detail)
        return responses.success_response(data=response.data)
    except ValidationError as e:
        return responses.fail_response(status_code=422,
                                       detail='Ошибка при валидации данных. Убедитесь, что вводите всё в соответствии с формой')


@router.post("/sign", description="Подписка на курс для начала прогресса в системе")
async def _(data: course_m.SignCourse, user: user_m.UserResponse = Depends(security.get_user)):
    material = user_m.UserAddProgress(
        user_id=user.user_id,
        material_id=data.course_id,
        material_type=MaterialTypes.COURSE,
        status=ProgressTypes.PROGRESS
    )
    result = await ProgressMethods.start_material(material)
    if isinstance(result, FailedResponse):
        detail = responses.fail_response(status_code=result.status_code, detail=result.detail)
        raise HTTPException(status_code=result.status_code, detail=detail)
    return responses.success_response(data=result.data)


@router.patch("/updateCourse", description="Изменение существующего курса")
async def _(data: course_m.UpdateCourse = Body(..., example=course_examples.UPDATE_COURSE),
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
    # Обновление материала
    response = await CourseMethods.update_course(data.course_id, changes=data.changes)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(response.status_code,
                                         detail=response.detail)
        raise HTTPException(response.status_code, detail=detail)
    return responses.success_response(data=response.data)


@router.delete("/deleteCourse", description="Удаление курса")
async def _(data: course_m.DeleteCourse, user: user_m.UserResponse = Depends(security.get_user)):
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
    # Удаление курса
    response = await CourseMethods.delete_course(data.course_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(response.status_code,
                                         detail=response.detail)
        raise HTTPException(response.status_code, detail=detail)
    return responses.success_response(data="Курс успешно удален!")
