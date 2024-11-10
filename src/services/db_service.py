import logging
from typing import Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from src.core.config import settings
from src.models import User, Coords, PerevalAdded, PerevalImages
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, Status, CoordsSchema, ImageSchema, UserSchema, SimpleResponse

logger = logging.getLogger("my_app")


class SubmitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pereval(self, data: SubmitDataRequest, user: User) -> Union[SubmitDataResponse, SimpleResponse]:
        """Создание нового перевала с координатами и изображениями."""
        try:
            # Проверка на существование перевала с таким же названием
            query = select(PerevalAdded).where(PerevalAdded.title == data.title)
            result = await self.db.execute(query)
            existing_pereval = result.scalars().first()

            if existing_pereval:
                raise HTTPException(status_code=400, detail=f"Перевал с названием '{data.title}' уже существует!")

            # Проверка на существование координат с такими же значениями
            coords_query = select(Coords).where(
                Coords.latitude == data.coords.latitude,
                Coords.longitude == data.coords.longitude,
                Coords.height == data.coords.height
            )
            coords_result = await self.db.execute(coords_query)
            existing_coords = coords_result.scalars().first()
            logger.info(f"Найденные координаты: {existing_coords.id if existing_coords else 'не найдены'}")

            if existing_coords:
                pereval_query = select(PerevalAdded).where(PerevalAdded.coord_id == existing_coords.id)
                result = await self.db.execute(pereval_query)
                pereval_records = result.scalars().all()

                if pereval_records:
                    logger.info(f"Найденные перевалы: {[{'id': p.id, 'title': p.title, 'status': p.status} for p in pereval_records]}")

                    existing_pereval = pereval_records[0]

                    return SimpleResponse(
                        message="Перевал с такими координатами уже существует.",
                        share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{existing_pereval.id}"
                    )

                raise HTTPException(status_code=404, detail="Перевал с такими координатами не найден")

            # Если координаты не существуют, создаем новые
            coords = Coords(
                latitude=data.coords.latitude,
                longitude=data.coords.longitude,
                height=data.coords.height
            )
            self.db.add(coords)
            await self.db.flush()

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
            self.db.add(pereval)
            await self.db.flush()

            # Сохраняем изображения
            images = []
            for img in data.images:
                image = PerevalImages(pereval_id=pereval.id, image_url=img.url)
                self.db.add(image)
                images.append(image)
            await self.db.flush()

            await self.db.commit()

            return SubmitDataResponse(
                message="Данные успешно отправлены",
                share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
                status=pereval.status,
                add_time=pereval.add_time,
                beauty_title=pereval.beauty_title,
                title=pereval.title,
                other_titles=pereval.other_titles,
                connect=pereval.connect,
                coords=CoordsSchema(
                    latitude=coords.latitude,
                    longitude=coords.longitude,
                    height=coords.height
                ),
                images=[ImageSchema(url=image.image_url) for image in images],
                user=UserSchema(
                    name=user.name,
                    email=user.email,
                    phone=user.phone
                )
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def update_pereval_status(self, pereval_id: int, status: Status):
        """Обновление статуса перевала."""
        async with self.db.begin():
            query = select(PerevalAdded).where(PerevalAdded.id == pereval_id)
            result = await self.db.execute(query)
            pereval = result.scalar_one_or_none()

            if not pereval:
                raise HTTPException(status_code=404, detail="Перевал не найден")

            # Проверка, можно ли изменить статус
            if pereval.status in [Status.accepted, Status.rejected]:
                raise HTTPException(status_code=400, detail="Статус нельзя изменить после модерации")

            pereval.status = status
            await self.db.flush()

        return {"message": "Статус обновлен", "pereval_id": pereval.id, "status": pereval.status}

    async def get_pereval(self, pereval_id: int) -> SubmitDataResponse:
        """Получение перевала с пользователем, координатами и изображениями."""
        query = select(PerevalAdded).options(
            joinedload(PerevalAdded.user),
            joinedload(PerevalAdded.coords),
            joinedload(PerevalAdded.images)
        ).where(PerevalAdded.id == pereval_id)

        result = await self.db.execute(query)
        pereval = result.unique().scalar_one_or_none()

        if not pereval:
            raise HTTPException(status_code=404, detail="Перевал не найден")

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
