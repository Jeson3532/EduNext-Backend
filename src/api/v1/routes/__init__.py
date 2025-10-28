from fastapi import APIRouter
from src.utils.logger import logger
from src.api.v1.routes.auth import router as auth_router


def get_routers():
    routers = list()
    for key, item in list(globals().items()):
        cond1 = '_router' in key
        cond2 = type(item) is APIRouter
        if cond1 and cond2:
            routers.append(item)
    return routers


if __name__ == '__main__':
    logger.info(f"Текущие роутеры: {get_routers()}")
