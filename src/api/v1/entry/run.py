from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from src.api.v1.routes import get_routers
from src.database import model as dbs
from fastapi.exceptions import RequestValidationError
import asyncio

app = FastAPI(title="Бэкенд для образовательной платформы с AI-репетитором")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        print(error["loc"])
        field = "".join(map(str, error["loc"][1]))
        msg = error["msg"]

        if error["type"] == "missing":
            msg = f"Поле {field} обязательно для заполнения."
        elif error["type"] == "string_pattern":
            msg = f"Поле {field} содержит недопустимые символы."

        errors.append({
            "field": field,
            "message": msg,
            "input": error.get("input", None)
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Произошла ошибка при валидации данных",
            "errors": errors
        }
    )

def add_routers(routs: list):
    return [app.include_router(router) for router in routs]

async def create_tables():
    await dbs.Users.create_table()
    await dbs.Course.create_table()
    await dbs.Lesson.create_table()
    await dbs.UserProgress.create_table()

# Инициализация роутеров
routers = get_routers()
add_routers(routers)

if __name__ == '__main__':
    asyncio.run(create_tables())
