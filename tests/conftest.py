import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db import get_async_session


# Фикстура для получения сессии
@pytest.fixture(scope="function")
async def async_session():
    async with get_async_session() as session:
        yield session


# Фикстура для транзакции
@pytest.fixture(scope="function")
async def transaction(async_session: AsyncSession):
    async with async_session.begin():
        yield async_session
        await async_session.rollback()
