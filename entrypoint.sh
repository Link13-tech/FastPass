#!/bin/sh

echo "Проверяем состояние миграций..."
MIGRATION_FILES=$(find alembic/versions -type f | wc -l)
# Проверяем текущую версию миграций в базе
CURRENT_VERSION=$(poetry run alembic current)

if [ -z "$CURRENT_VERSION" ]; then
    # База пустая, создаём первую миграцию и применяем её
    echo "База пустая. Создаём первую миграцию..."
    poetry run alembic revision --autogenerate -m "Initial migration"
    poetry run alembic upgrade head
elif [ "$MIGRATION_FILES" -eq 0 ] && [ -n "$CURRENT_VERSION" ]; then
    # Папка пуста, но база имеет миграцию, синхронизируем с помощью stamp
    echo "Папка версий пуста, синхронизируем состояние с базой..."
    poetry run alembic stamp head   # Обновляем таблицу alembic_version, чтобы указать, что миграция уже применена
    echo "Создаём новую миграцию с учётом изменений в моделях(есл они были)..."
    poetry run alembic revision --autogenerate -m "Auto migration update"
    poetry run alembic upgrade head
else
    echo "Миграции были применены. Текущая версия: $CURRENT_VERSION"
fi

echo "Запускаем приложение..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8080
