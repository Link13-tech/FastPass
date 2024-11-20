#!/bin/sh

echo "Проверяем состояние миграций..."

# Получаем текущую версию миграции из базы данных
CURRENT_VERSION=$(poetry run alembic current | awk '{print $1}')

# Получаем последнюю версию миграции из папки alembic/versions
LATEST_VERSION=$(ls alembic/versions/*.py | tail -n 1 | awk -F'_' '{print $1}' | xargs basename)

# Эхо текущих версий
echo "Текущая версия миграции в базе данных: $CURRENT_VERSION"
echo "Последняя версия миграции в папке: $LATEST_VERSION"

# Если база пуста, применяем все миграции
if [ -z "$CURRENT_VERSION" ]; then
    echo "База данных пуста. Применяем все миграции из репозитория..."
    poetry run alembic upgrade head
elif [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Версия базы данных ($CURRENT_VERSION) отличается от последней миграции ($LATEST_VERSION). Применяем миграции..."
    poetry run alembic upgrade head
else
    echo "Все миграции уже применены. Версия базы данных: $CURRENT_VERSION."
fi

echo "Запускаем приложение..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8080