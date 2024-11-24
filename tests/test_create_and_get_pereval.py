import pytest
from httpx import AsyncClient
from httpx import ASGITransport


from main import app


@pytest.mark.asyncio
async def test_create_and_get_pereval(create_pereval):
    submit_data = await create_pereval

    # Отправляем запрос для создания перевала
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/submit/submitData", json=submit_data)

        # Проверяем, что запрос прошел успешно и данные созданы
        assert response.status_code == 200
        data = response.json()
        assert "share_link" in data
        assert data["message"] == "Данные успешно отправлены"
        pereval_id = data["share_link"].split("/")[-1]

        # Получаем данные о перевале по ID
        response_get = await client.get(f"/submit/submitData/{pereval_id}")
        assert response_get.status_code == 200
        pereval_data = response_get.json()
        assert pereval_data["title"] == submit_data["title"]
