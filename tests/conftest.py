import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db import get_async_session
from faker import Faker
import random

fake = Faker()


# Фикстура для получения сессии
@pytest.fixture(scope="function")
async def async_session():
    async with get_async_session() as session:
        yield session


# Фикстура для транзакции
@pytest.fixture(scope="function")
async def transaction(async_session: AsyncSession):
    try:
        async with async_session.begin():
            yield async_session
    finally:
        await async_session.rollback()


# Фикстура для создания перевала
@pytest.fixture
async def create_pereval(transaction: AsyncSession):
    # Генерация данных для перевала
    submit_data = {
        "user": {
            "email": fake.email(),
            "fam": fake.last_name(),
            "name": fake.first_name(),
            "otc": fake.first_name_male(),
            "phone": fake.phone_number(),
        },
        "title": f"Test Pereval {random.randint(1, 1000)}",
        "beauty_title": f"Красивый перевал {random.randint(1, 1000)}",
        "other_titles": f"Переход {random.randint(1, 1000)}, Тур 2024",
        "connect": fake.text(max_nb_chars=50),
        "coords": {
            "latitude": round(random.uniform(-90, 90), 4),
            "longitude": round(random.uniform(-180, 180), 4),
            "height": random.randint(100, 3000),
        },
        "level": {
            "winter": random.choice(["3A", "3B", "2A", "2B"]),
            "summer": random.choice(["2A", "2B", "1A", "1B"]),
            "autumn": random.choice(["1A", "1B", "2A"]),
            "spring": random.choice(["2A", "2B", "1A"]),
        },
        "images": [
            {"url": fake.image_url(), "title": f"Image {random.randint(1, 100)}"},
            {"url": fake.image_url(), "title": f"Image {random.randint(101, 200)}"},
        ],
    }
    return submit_data
