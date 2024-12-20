
# Fast Pass API

Fast Pass API — это REST API для работы с перевалами, включая создание, получение, обновление и управление их статусами.

## Основной функционал:
- Создание записи перевала.
- Получение всех перевалов.
- Получение перевалов по email пользователя.
- Получение перевала по ID.
- Обновление перевала.
- Обновление статуса перевала.

---

## Структура проекта

- **src/api** — обработчики запросов (endpoints).
- **src/core** — конфигурационные файлы.
- **src/db** — взаимодействие с базой данных.
- **src/models** — модели данных.
- **src/schemas** — схемы данных.
- **src/services** — бизнес-логика.

---

## Swagger UI

После запуска приложения документация доступна по адресу [http://localhost:8080/api/openapi](http://localhost:8080/api/openapi).

Альтернатива [http://localhost:8080/redoc](http://localhost:8080/redoc).

---

## Хостинг (Пример с Railway.app)

Пример вызова документации опубликованного API:
- URL: [https://fastpass-production.up.railway.app/api/openapi](https://fastpass-production.up.railway.app/api/openapi).

Альтернатива:
- URL: [https://fastpass-production.up.railway.app/redoc](https://fastpass-production.up.railway.app/redoc).
---
