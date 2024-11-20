# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt update && apt install -y gcc libpq-dev iputils-ping telnet postgresql-client

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файлы зависимостей, чтобы кэшировать установку зависимостей
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости с помощью Poetry (по умолчанию Poetry создаст виртуальное окружение)
RUN poetry install --no-dev

# Копируем остальные файлы проекта
COPY . /app/

# Инициализируем Alembic (создание папки alembic, конфигурации и файла env.py)
RUN poetry run alembic init -t async alembic

# Удаляем строку с sqlalchemy.url из alembic.ini
RUN sed -i '/sqlalchemy.url/d' alembic.ini

# Генерация нового env.py с подключением к базе данных
RUN echo "\
import asyncio\n\
from logging.config import fileConfig\n\
\n\
from sqlalchemy import pool\n\
from sqlalchemy.engine import Connection\n\
from sqlalchemy.ext.asyncio import async_engine_from_config\n\
\n\
from src.core.config import settings\n\
from src.models import Base\n\
from alembic import context\n\
\n\
config = context.config\n\
config.set_main_option('sqlalchemy.url', str(settings.postgres_dsn))\n\
if config.config_file_name is not None:\n\
    fileConfig(config.config_file_name)\n\
target_metadata = Base.metadata\n\
\n\
def run_migrations_offline() -> None:\n\
    url = config.get_main_option('sqlalchemy.url')\n\
    context.configure(\n\
        url=url,\n\
        target_metadata=target_metadata,\n\
        literal_binds=True,\n\
        dialect_opts={'paramstyle': 'named'},\n\
    )\n\
    with context.begin_transaction():\n\
        context.run_migrations()\n\
\n\
def do_run_migrations(connection: Connection) -> None:\n\
    context.configure(connection=connection, target_metadata=target_metadata)\n\
    with context.begin_transaction():\n\
        context.run_migrations()\n\
\n\
async def run_async_migrations() -> None:\n\
    connectable = async_engine_from_config(\n\
        config.get_section(config.config_ini_section, {}),\n\
        prefix='sqlalchemy.',\n\
        poolclass=pool.NullPool,\n\
    )\n\
    async with connectable.connect() as connection:\n\
        await connection.run_sync(do_run_migrations)\n\
    await connectable.dispose()\n\
\n\
def run_migrations_online() -> None:\n\
    asyncio.run(run_async_migrations())\n\
\n\
if context.is_offline_mode():\n\
    run_migrations_offline()\n\
else:\n\
    run_migrations_online()" > /app/alembic/env.py

# Создаем директорию для логов (если используется логирование в файлы)
RUN mkdir -p /app/logs && chmod -R 755 /app/logs

# Открываем порт для приложения
EXPOSE 8080

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Добавляем volume для хранения миграций и базы данных
VOLUME ["/app/alembic/versions"]

CMD ["/app/entrypoint.sh"]