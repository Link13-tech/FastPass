#!/bin/sh

# Проверяем текущую версию базы данных
CURRENT_VERSION=$(alembic current | grep "head")

if [ -n "$CURRENT_VERSION" ]; then
    echo "Миграции уже применены, пропускаем создание и применение."
else
    echo "Создаём первую миграцию и применяем её..."
    alembic revision --autogenerate -m 'Initial migration'
    alembic upgrade head
fi

# Запускаем приложение
echo "Запуск приложения..."
uvicorn main:app --host 0.0.0.0 --port 8080