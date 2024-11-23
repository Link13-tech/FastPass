import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from faker import Faker
import random

fake = Faker()


@pytest.mark.asyncio
async def test_create_and_get_pereval(transaction: AsyncSession):
    # Генерируем случайные данные для перевала
    submit_data = {
        "user": {
            "email": fake.email(),
            "fam": fake.last_name(),
            "name": fake.first_name(),
            "otc": fake.first_name_male(),
            "phone": fake.phone_number()
        },
        "title": f"Test Pereval {random.randint(1, 1000)}",
        "beauty_title": f"Красивый перевал {random.randint(1, 1000)}",
        "other_titles": f"Переход {random.randint(1, 1000)}, Тур 2024",
        "connect": fake.text(max_nb_chars=50),
        "coords": {
            "latitude": round(random.uniform(-90, 90), 4),
            "longitude": round(random.uniform(-180, 180), 4),
            "height": random.randint(100, 3000)
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

    # Отправляем запрос для создания перевала
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/submit/submitData", json=submit_data)

        # Проверяем, что запрос прошел успешно и данные созданы
        assert response.status_code == 200
        data = response.json()
        assert "share_link" in data
        assert data["message"] == "Данные успешно отправлены"
        pereval_id = data["share_link"].split("/")[-1]  # Извлекаем ID из ссылки

        # Получаем данные о перевале по ID
        response_get = await client.get(f"/submit/submitData/{pereval_id}")
        assert response_get.status_code == 200
        pereval_data = response_get.json()
        assert pereval_data["title"] == submit_data["title"]
