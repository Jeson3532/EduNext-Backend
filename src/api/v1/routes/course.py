from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas import course_schema as course_m, user_schema as user_m
from src.api.v1.methods import security
from src.api.v1 import responses
from src.database.methods import CourseMethods
from src.database.responses import FailedResponse

router = APIRouter(prefix="/api/v1/course", tags=['Курсы', 'Courses'])


@router.post("/addCourse")
async def _(data: course_m.CourseResponse, user: user_m.UserResponse = Depends(security.get_user)):
    course = course_m.CourseAddModel(
        course_title=data.course_title,
        author=user.username,
        desc=data.desc,
        course_categories=data.course_categories,
    )
    response = await CourseMethods.add_course(course)
    if isinstance(response, FailedResponse):
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return responses.success_response(data={"message": "Курс успешно создан", "course": course})
