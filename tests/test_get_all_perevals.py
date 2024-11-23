import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from faker import Faker
import random

fake = Faker()


@pytest.mark.asyncio
async def test_get_all_perevals(transaction: AsyncSession):
    submit_data_list = []

    # Генерация данных для отправки
    for _ in range(3):
        submit_data = {
            "user": {
                "email": fake.email(),
                "fam": fake.last_name(),
                "name": fake.first_name(),
                "otc": fake.first_name_male(),
                "phone": fake.phone_number()
            },
            "title": f"Test Pereval {random.randint(3000, 10000)}",
            "beauty_title": f"Красивый перевал {random.randint(1, 1000)}",
            "other_titles": f"Переход {random.randint(1, 1000)}, Тур 2024",
            "connect": fake.text(max_nb_chars=50),
            "coords": {
                "latitude": round(random.uniform(-190, 190), 4),
                "longitude": round(random.uniform(-1800, 1800), 4),
                "height": random.randint(100, 5000)
            },
            "level": {
                "winter": random.choice(["3A", "3B", "2A", "2B"]),
                "summer": random.choice(["2A", "2B", "1A", "1B"]),
                "autumn": random.choice(["1A", "1B", "2A"]),
                "spring": random.choice(["2A", "2B", "1A"])
            },
            "images": [
                {"url": fake.image_url(), "title": f"Image {random.randint(1, 100)}"},
                {"url": fake.image_url(), "title": f"Image {random.randint(101, 200)}"}
            ]
        }
        submit_data_list.append(submit_data)

    # Отправляем несколько запросов для создания перевалов
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        for submit_data in submit_data_list:
            response = await client.post("/submit/submitData", json=submit_data)
            assert response.status_code == 200, f"Failed to create pereval: {response.text}"

        # Получаем все перевалы
        response_get_all = await client.get("/submit/submitData/")
        assert response_get_all.status_code == 200, f"Failed to get all perevals: {response_get_all.text}"

        # Проверяем, что результат - это список и что в нем есть элементы
        result = response_get_all.json()
        assert isinstance(result, list), "Expected a list of perevals"
        assert len(result) >= 3, f"Expected at least 3 perevals, but got {len(result)}"
