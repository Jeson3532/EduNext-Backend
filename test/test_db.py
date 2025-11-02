import pytest
import asyncio
# from src.database.config import DBConfig
from sqlalchemy import text
from src.database.model import engine
from src.utils.logger import logger

@pytest.mark.asyncio
async def test_connect():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        scalar = result.scalar()
        assert scalar == 1

