import logging
from typing import Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from src.core.config import settings
from src.models import User, Coords, PerevalAdded, PerevalImages, Level
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, Status, CoordsSchema, ImageSchema, UserSchema, SimpleResponse, LevelSchema

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

            logger.info("Создание записи уровня сложности")
            level = Level(
                winter=data.level.winter,
                summer=data.level.summer,
                autumn=data.level.autumn,
                spring=data.level.spring
            )

            self.db.add(level)
            await self.db.flush()
            logger.info(f"Уровень сложности успешно добавлен с ID: {level.id}")

            # Создаем запись о перевале
            logger.info(f"Создание перевала: {data.title} для пользователя {user.email}")
            pereval = PerevalAdded(
                user_id=user.id,
                coord_id=coords.id,
                level_id=level.id,
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
                image = PerevalImages(pereval_id=pereval.id, image_url=img.url, title=img.title)
                self.db.add(image)
                images.append(image)
            await self.db.flush()

            await self.db.commit()

            return SubmitDataResponse(
                message="Данные успешно отправлены",
                share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
                status=pereval.status,
                beauty_title=pereval.beauty_title,
                title=pereval.title,
                other_titles=pereval.other_titles,
                connect=pereval.connect,
                add_time=pereval.add_time,
                user=UserSchema(
                    fam=user.fam,
                    name=user.name,
                    otc=user.otc,
                    email=user.email,
                    phone=user.phone
                ),
                coords=CoordsSchema(
                    latitude=coords.latitude,
                    longitude=coords.longitude,
                    height=coords.height
                ),
                level=LevelSchema(
                    winter=level.winter,
                    summer=level.summer,
                    autumn=level.autumn,
                    spring=level.spring
                ),
                images=[ImageSchema(url=image.image_url, title=image.title) for image in images],
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
        """Получение перевала с пользователем, координатами и изображениями и сложностью."""
        query = select(PerevalAdded).options(
            joinedload(PerevalAdded.user),
            joinedload(PerevalAdded.coords),
            joinedload(PerevalAdded.level),
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
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            add_time=pereval.add_time,
            user=UserSchema(
                fam=pereval.user.fam,
                name=pereval.user.name,
                otc=pereval.user.otc,
                email=pereval.user.email,
                phone=pereval.user.phone
            ),
            coords=CoordsSchema(
                latitude=pereval.coords.latitude,
                longitude=pereval.coords.longitude,
                height=pereval.coords.height
            ),
            level=LevelSchema(
                winter=pereval.level.winter,
                summer=pereval.level.summer,
                autumn=pereval.level.autumn,
                spring=pereval.level.spring
            ),
            images=[ImageSchema(url=image.image_url, title=image.title) for image in pereval.images],
        )
