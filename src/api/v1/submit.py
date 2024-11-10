import logging
from typing import Union

from fastapi import APIRouter

from src.models.pereval import Status
from src.db.db import db_dependency
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, SimpleResponse
from src.services.db_service import SubmitService
from src.services.user_service import get_or_create_user

submit_router = APIRouter(prefix="/submit", tags=["submit"])
logger = logging.getLogger("my_app")


@submit_router.post("/create", response_model=Union[SubmitDataResponse, SimpleResponse], name="Создать перевал")
async def create_pereval(data: SubmitDataRequest, db: db_dependency):
    logger.info(f"Создание перевала для пользователя с email: {data.user.email}")

    # Создаем или находим пользователя
    user = await get_or_create_user(db, data.user)

    # Создаем экземпляр сервиса
    service = SubmitService(db)

    # Используем сервис для создания перевала
    return await service.create_pereval(data, user)


@submit_router.get("/get/{pereval_id}", response_model=SubmitDataResponse, name="Получить перевал")
async def get_pereval(pereval_id: int, db: db_dependency):
    logger.info(f"Получение перевала с ID: {pereval_id}")

    service = SubmitService(db)
    return await service.get_pereval(pereval_id)


@submit_router.patch("/update-status/{pereval_id}", name="Обновить статус перевала")
async def update_pereval_status(pereval_id: int, status: Status, db: db_dependency):
    logger.info(f"Обновление статуса перевала с ID: {pereval_id} на {status}")

    service = SubmitService(db)
    return await service.update_pereval_status(pereval_id, status)
