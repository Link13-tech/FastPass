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

# Открываем порт для приложения
EXPOSE 8080

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]