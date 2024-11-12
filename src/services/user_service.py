import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.schemas.submit import UserSchema

logger = logging.getLogger("my_app")


# Функция для создания или получения пользователя
async def get_or_create_user(db: AsyncSession, user_data: UserSchema) -> User:
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        if not user:
            user = User(
                fam=user_data.fam,
                name=user_data.name,
                otc=user_data.otc,
                email=user_data.email,
                phone=user_data.phone
            )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Создан новый пользователь с email: {user.email.encode('utf-8', 'ignore').decode('utf-8')}")
    else:
        logger.info(f"Пользователь с email {user.email} найден")
    return user
