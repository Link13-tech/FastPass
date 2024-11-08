import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("FSTR_DB_LOGIN")
DB_PASSWORD = os.getenv("FSTR_DB_PASS")
DB_HOST = os.getenv("FSTR_DB_HOST")
DB_PORT = os.getenv("FSTR_DB_PORT")
DB_NAME = os.getenv("FSTR_DB_NAME")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_session_maker() as session:
        yield session
