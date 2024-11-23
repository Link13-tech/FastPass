import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from faker import Faker
import random

fake = Faker()


@pytest.mark.asyncio
async def test_get_perevals_by_user_email(transaction: AsyncSession):
    # Генерируем случайные данные для пользователя
    user_data = {
        "email": fake.email(),
        "fam": fake.last_name(),
        "name": fake.first_name(),
        "otc": fake.first_name_male(),
        "phone": fake.phone_number()
    }

    submit_data_list = []
    for _ in range(3):  # Создаем 3 перевала для одного пользователя
        submit_data = {
            "user": user_data,
            "title": f"Test Pereval {random.randint(2000, 10000)}",
            "beauty_title": f"Красивый перевал {random.randint(1, 1000)}",
            "other_titles": f"Переход {random.randint(1, 1000)}, Тур 2024",
            "connect": fake.text(max_nb_chars=50),
            "coords": {
                "latitude": round(random.uniform(-1000, 1000), 4),
                "longitude": round(random.uniform(-1800, 1800), 4),
                "height": random.randint(100, 10000)
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

    # Отправляем запросы на создание перевалов
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        for submit_data in submit_data_list:
            response = await client.post("/submit/submitData", json=submit_data)
            assert response.status_code == 200
            data = response.json()
            assert "share_link" in data

        # Получаем перевалы по email
        response_get = await client.get(f"/submit/submitData/by_user/?user__email={user_data['email']}")
        assert response_get.status_code == 200
        result = response_get.json()

        assert len(result) == 3
        assert all(item["user"]["email"] == user_data['email'] for item in result)
