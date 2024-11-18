# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt update && apt install -y gcc libpq-dev

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файлы зависимостей, чтобы кэшировать установку зависимостей
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости с помощью Poetry (по умолчанию Poetry создаст виртуальное окружение)
RUN poetry install --no-dev

# Проверим, что alembic доступен
RUN poetry run alembic --version

# Копируем остальные файлы проекта
COPY . /app/


# Создаем директорию для логов (если используется логирование в файлы)
RUN mkdir -p /app/logs && chmod -R 755 /app/logs

# Открываем порт для приложения
EXPOSE 8080

# Команда для запуска приложения
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8080"]