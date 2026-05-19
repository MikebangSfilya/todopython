# Task Tracker API

Task Tracker API — сервис для управления задачами. Пользователь может создавать задачи, задавать дедлайны, статусы и приоритеты, группировать задачи по категориям, добавлять метки, оставлять комментарии и смотреть статистику выполнения.

Проект включает REST API, JWT-авторизацию, Swagger-документацию, Django Admin и простой одностраничный интерфейс для проверки основных сценариев.

## Возможности

- регистрация пользователей;
- авторизация по JWT;
- создание, просмотр, изменение и удаление задач;
- статусы задач: к выполнению, в работе, готово;
- приоритеты задач: низкий, средний, высокий;
- дедлайны;
- категории;
- метки;
- комментарии к задачам;
- фильтрация и поиск задач;
- статистика по задачам;
- Swagger UI;
- Django Admin;
- простой frontend на одной странице.

## Стек

- Python 3.12;
- Django 5.2;
- Django REST Framework;
- Simple JWT;
- Pydantic;
- django-filter;
- drf-spectacular;
- PostgreSQL;
- Docker Compose;
- uv.

## Структура проекта

```text
config/                 настройки Django-проекта
todos/models.py         модели базы данных
todos/schemas.py        Pydantic-схемы входных данных
todos/services.py       сервисный слой
todos/presenters.py     подготовка HTTP-ответов
todos/validation.py     обработка ошибок валидации
todos/views.py          API endpoints
todos/serializers.py    схемы для Swagger/OpenAPI
templates/index.html    одностраничный frontend
```

Runtime-валидация и бизнес-логика выполняются через Pydantic-схемы и сервисный слой. DRF-сериализаторы оставлены для описания схемы API в Swagger.

## Запуск через Docker

```bash
docker compose up -d --build
```

После запуска:

```text
Frontend:    http://127.0.0.1:8000/
Swagger UI:  http://127.0.0.1:8000/api/schema/swagger-ui/
Admin:       http://127.0.0.1:8000/admin/
```

При запуске через Docker используется PostgreSQL. Миграции применяются автоматически при старте `web`-контейнера.

## Переменные окружения

Пример настроек находится в `.env.example`.

```bash
cp .env.example .env
```

Основные переменные:

```env
SECRET_KEY=django-insecure-change-me
DJANGO_DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
APP_PORT=8000
DB_NAME=todo_db
DB_USER=todo_user
DB_PASSWORD=todo_pass
DB_HOST=db
DB_PORT=5432
```

## Локальный запуск без Docker

```bash
uv sync
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Если `DB_HOST` не задан, проект использует SQLite.

## Основные API endpoints

Регистрация:

```text
POST /api/register/
```

JWT:

```text
POST /api/token/
POST /api/token/refresh/
```

Задачи:

```text
GET    /api/tasks/
POST   /api/tasks/
GET    /api/tasks/{id}/
PATCH  /api/tasks/{id}/
DELETE /api/tasks/{id}/
POST   /api/tasks/{id}/complete/
POST   /api/tasks/{id}/reopen/
GET    /api/tasks/stats/
```

Категории:

```text
GET    /api/categories/
POST   /api/categories/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/
```

Метки:

```text
GET    /api/labels/
POST   /api/labels/
PATCH  /api/labels/{id}/
DELETE /api/labels/{id}/
```

Комментарии:

```text
GET    /api/comments/
POST   /api/comments/
PATCH  /api/comments/{id}/
DELETE /api/comments/{id}/
```

## Примеры запросов

Регистрация:

```http
POST /api/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "N7v!q2Lz#p9R4mT"
}
```

Получение JWT-токена:

```http
POST /api/token/
Content-Type: application/json

{
  "username": "testuser",
  "password": "N7v!q2Lz#p9R4mT"
}
```

Создание задачи:

```http
POST /api/tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Подготовить отчет",
  "description": "Собрать материалы и проверить дедлайн",
  "deadline": "2026-05-25T18:00:00Z",
  "status": "todo",
  "priority": "high",
  "label_ids": []
}
```

Фильтрация задач:

```text
GET /api/tasks/?status=todo
GET /api/tasks/?priority=high
GET /api/tasks/?search=отчет
GET /api/tasks/?deadline__gte=2026-05-20T00:00:00Z
GET /api/tasks/?ordering=deadline
```

## Проверка проекта

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py spectacular --validate --file /tmp/schema.yaml
```
