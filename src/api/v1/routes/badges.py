from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from src.api.v1.schemas import lesson_schema as lesson_m, user_schema as user_m, tasks_schema as task_m
from src.api.v1.methods import security
from src.api.v1 import responses
from src.database.methods import BadgeMethods
from src.database.responses import FailedResponse
from src.api.v1.enums import LessonTypes as lt, MaterialTypes, ProgressTypes
from src.ai_agent.yandex_gpt import get_answer_ai, generate_task, compare_answers
from src.api.v1.examples import lesson_examples
import json
from src.badges.dispatcher import BadgeDispatcher
from src.badges.status import BadgeScanStatus

router = APIRouter(prefix="/api/v1/badge", tags=['Достижения', 'Achievements'])


@router.get("/myBadges")
async def _(user: user_m.UserResponse = Depends(security.get_user)):
    response = await BadgeMethods.get_user_badges(user.user_id)
    if isinstance(response, FailedResponse):
        detail = responses.fail_response(status_code=response.status_code, detail=response.detail)
        raise HTTPException(status_code=response.status_code, detail=detail)
    return responses.success_response(data=response.data)
