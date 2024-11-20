#!/bin/sh

echo "Проверяем состояние миграций..."
if poetry run alembic current | grep "head"; then
    echo "Миграции уже применены."
else
    echo "Создаём и применяем миграции..."
    poetry run alembic revision --autogenerate -m "Initial migration"
    poetry run alembic upgrade head
fi

# Запускаем приложение
echo "Запуск приложения..."
uvicorn main:app --host 0.0.0.0 --port 8080