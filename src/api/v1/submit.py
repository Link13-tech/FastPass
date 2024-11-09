from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging
from src.core.config import settings
from src.db.db import db_dependency
from src.models import User, Coords, PerevalAdded, PerevalImages
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, UserSchema, Status, CoordsSchema, ImageSchema

submit_router = APIRouter(prefix="/submit", tags=['submit'])
logger = logging.getLogger("my_app")


# Функция для поиска или создания пользователя
async def get_or_create_user(db, user_data: UserSchema) -> User:
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        logger.info(f"Создание нового пользователя с email: {user_data.email}")
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone
        )
        db.add(user)
        await db.flush()  # flush, чтобы изменения были синхронизированы с базой данных, но не зафиксированы
    else:
        logger.info(f"Пользователь найден: {user.id}")

    return user


# Эндпоинт для создания нового перевала
@submit_router.post("/create", response_model=SubmitDataResponse, name="Создать перевал")
async def create_pereval(
    data: SubmitDataRequest,
    db: db_dependency
):
    logger.info(f"Создание перевала для пользователя с email: {data.user.email}")

    try:
        # Создаем или получаем пользователя
        user = await get_or_create_user(db, data.user)

        # Создаем запись координат
        coords = Coords(
            latitude=data.coords.latitude,
            longitude=data.coords.longitude,
            height=data.coords.height
        )
        db.add(coords)
        await db.flush()  # flush после добавления координат

        # Создаем запись о перевале
        pereval = PerevalAdded(
            user_id=user.id,
            coord_id=coords.id,
            beauty_title=data.beauty_title,
            title=data.title,
            other_titles=data.other_titles,
            connect=data.connect,
            status=Status.new
        )
        db.add(pereval)
        await db.flush()  # flush после добавления перевала

        # Сохраняем изображения, связанные с перевалом
        for img in data.images:
            image = PerevalImages(pereval_id=pereval.id, image_url=img.url)
            db.add(image)
        await db.flush()  # flush после добавления изображений

        # Применяем изменения в БД
        await db.commit()  # окончательное сохранение изменений

        return SubmitDataResponse(
            message="Данные успешно отправлены",
            share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
            status=pereval.status,
            add_time=pereval.add_time
        )

    except Exception as e:
        logger.error(f"Ошибка при создании перевала: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании данных")


# Эндпоинт для обновления статуса перевала
@submit_router.patch("/update_status/{pereval_id}", name="Обновить статус перевала")
async def update_status(
    pereval_id: int,
    status: Status,
    db: db_dependency
):
    logger.info(f"Обновление статуса перевала с ID: {pereval_id} на {status}")

    async with db.begin():
        query = select(PerevalAdded).where(PerevalAdded.id == pereval_id)
        result = await db.execute(query)
        pereval = result.scalar_one_or_none()

        if not pereval:
            raise HTTPException(status_code=404, detail="Перевал не найден")

        # Проверка, можно ли изменить статус
        if pereval.status in [Status.accepted, Status.rejected]:
            raise HTTPException(status_code=400, detail="Статус нельзя изменить после модерации")

        pereval.status = status
        await db.commit()

    return {"message": "Статус обновлен", "pereval_id": pereval.id, "status": pereval.status}


@submit_router.get("/get/{pereval_id}", response_model=SubmitDataResponse, name="Получить перевал")
async def get_pereval(pereval_id: int, db: db_dependency):
    logger.info(f"Получение данных перевала с ID: {pereval_id}")

    try:
        # Формируем запрос с подгрузкой связанных данных
        query = select(PerevalAdded).options(
            joinedload(PerevalAdded.user),
            joinedload(PerevalAdded.coords),
            joinedload(PerevalAdded.images)
        ).where(PerevalAdded.id == pereval_id)

        result = await db.execute(query)
        pereval = result.unique().scalar_one_or_none()

        if not pereval:
            raise HTTPException(status_code=404, detail="Перевал не найден")

        # Формируем ответ с вложенными данными
        return SubmitDataResponse(
            message="Данные перевала",
            share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
            status=pereval.status,
            add_time=pereval.add_time,
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            coords=CoordsSchema(
                latitude=pereval.coords.latitude,
                longitude=pereval.coords.longitude,
                height=pereval.coords.height
            ),
            images=[ImageSchema(url=image.image_url) for image in pereval.images],
            user=UserSchema(
                name=pereval.user.name,
                email=pereval.user.email,
                phone=pereval.user.phone
            )
        )

    except Exception as e:
        logger.error(f"Ошибка при получении данных перевала: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных перевала")
