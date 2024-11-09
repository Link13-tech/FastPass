# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy import insert
# from src.db.db import async_session
# from src.models.user import User
# from src.models.coords import Coords
# from src.models.pereval import PerevalAdded, Status
# from src.models.images import PerevalImages
# from typing import Optional
#
#
# class DatabaseService:
#     def __init__(self):
#         self.session: Optional[AsyncSession] = None
#
#     async def __aenter__(self):
#         self.session = async_session()
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self.session.close()
#
#     async def add_user(self, name: str, email: str, phone: str) -> User:
#         """Добавляет пользователя в таблицу users."""
#         new_user = User(name=name, email=email, phone=phone)
#         self.session.add(new_user)
#         await self.session.commit()
#         await self.session.refresh(new_user)
#         return new_user
#
#     async def add_coords(self, latitude: float, longitude: float, height: int) -> Coords:
#         """Добавляет координаты в таблицу coords."""
#         new_coords = Coords(latitude=latitude, longitude=longitude, height=height)
#         self.session.add(new_coords)
#         await self.session.commit()
#         await self.session.refresh(new_coords)
#         return new_coords
#
#     async def add_pereval(self, user_id: int, coord_id: int, beauty_title: str, title: str,
#                           other_titles: str, connect: str) -> PerevalAdded:
#         """Добавляет перевал в таблицу pereval_added с установленным статусом new."""
#         new_pereval = PerevalAdded(
#             user_id=user_id,
#             coord_id=coord_id,
#             beauty_title=beauty_title,
#             title=title,
#             other_titles=other_titles,
#             connect=connect,
#             status=Status.new
#         )
#         self.session.add(new_pereval)
#         await self.session.commit()
#         await self.session.refresh(new_pereval)
#         return new_pereval
#
#     async def add_image(self, pereval_id: int, image_url: str) -> PerevalImages:
#         """Добавляет изображение для перевала."""
#         new_image = PerevalImages(pereval_id=pereval_id, image_url=image_url)
#         self.session.add(new_image)
#         await self.session.commit()
#         await self.session.refresh(new_image)
#         return new_image
