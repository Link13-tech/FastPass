import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.schemas.submit import UserSchema

logger = logging.getLogger("my_app")


# ������� ��� �������� ��� ��������� ������������
async def get_or_create_user(db: AsyncSession, user_data: UserSchema) -> User:
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # ���� ������������ �� ������, ������� ������
    if not user:
        user = User(name=user_data.name, email=user_data.email, phone=user_data.phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    #     logger.info(f"������ ����� ������������ � email: {user.email}")
    # else:
    #     logger.info(f"������������ � email {user.email} ������")
    return user
