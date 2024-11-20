#!/bin/sh

echo "Проверяем состояние миграций..."

# Получаем текущую версию миграций в базе данных
CURRENT_VERSION=$(poetry run alembic current)

# Если версия не найдена или это первый запуск, создаем миграцию
if [ -z "$CURRENT_VERSION" ] || [ "$CURRENT_VERSION" == "0" ]; then
    echo "Миграции не найдены или это первый запуск, создаем и применяем миграции..."
    # Создаем миграцию и применяем её
    poetry run alembic revision --autogenerate -m "Initial migration"
    poetry run alembic upgrade head
else
    echo "Миграции уже применены. Текущая версия: $CURRENT_VERSION"
fi

# Запускаем приложение
echo "Запускаем приложение..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8080