# ShortLink

Небольшой сервис на FastAPI для сокращения ссылок.

Что есть сейчас:
- создание короткой ссылки;
- редирект по `short_id`;
- статистика по ссылке (`count_redirect`, даты, статус);
- CRUD для постов;
- кэш постов в Redis.

## Что нужно для запуска

- Docker + Docker Compose
- внешняя docker-сеть `backend_network`

Если сети нет:

```bash
docker network create backend_network
```

## Запуск в Docker

Из корня проекта:

```bash
docker compose up -d --build
```

Проверить логи приложения:

```bash
docker logs -f short_link_project
```

Остановка:

```bash
docker compose down
```

## Адреса

- API: `http://localhost:8010`
- Swagger: `http://localhost:8010/api/docs`
- OpenAPI JSON: `http://localhost:8010/api/openapi.json`

Префикс API в роутерах: `/api/v1`.

## Основные роуты

### Link
- `POST /api/v1/link/shorten` — создать короткую ссылку
- `GET /api/v1/link/{short_id}` — редирект на оригинальный URL
- `GET /api/v1/link/stats/{short_id}` — статистика ссылки
- `GET /api/v1/link/shorts` — список ссылок
- `PATCH /api/v1/link/update/{short_id}` — обновить ссылку
- `DELETE /api/v1/link/delete/{short_id}` — удалить ссылку

### Post
- `POST /api/v1/post/create` — создать пост
- `GET /api/v1/post/post/{post_id}` — получить пост по id
- `GET /api/v1/post/posts` — список постов
- `PATCH /api/v1/post/update/{post_id}` — обновить пост
- `DELETE /api/v1/post/delete/{post_id}` — удалить пост

## Переменные окружения (`.env`)

Ниже минимальный набор, который реально используется.

### База данных
- `DB_DRIVER` — SQLAlchemy driver, обычно `postgresql+asyncpg`
- `DB_USER` — пользователь БД
- `DB_PASSWORD` — пароль БД
- `DB_HOST` — хост БД (в docker-compose это `db`)
- `DB_PORT` — порт БД (в проекте сейчас `5433`)
- `DB_NAME` — имя базы
- `DB_URL` — полный DSN для Alembic/подключения

### Redis
- `REDIS_PATH` — URL Redis, например `redis://redis:6379`
- `REDIS_DB` — номер базы Redis (например `1`)
- `REDIS_PASSWORD` — пароль Redis (если используется)
- `REDIS_USER` — пользователь Redis ACL (если используется)
- `REDIS_USER_PASSWORD` — пароль пользователя Redis ACL (если используется)

### Ограничения длины
- `LENGTH_SHORT_ID` — длина short id
- `LENGHT_TITLE_POST` — лимит заголовка поста
- `LENGHT_DESCRIPTION_POST` — лимит описания поста


## Пример `.env`

```env
DB_DRIVER=postgresql+asyncpg
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5433
DB_NAME=short_link
DB_URL=postgresql+asyncpg://postgres:postgres@db:5433/short_link

REDIS_PATH=redis://redis:6379
REDIS_DB=1
REDIS_PASSWORD=redis
REDIS_USER=redis
REDIS_USER_PASSWORD=redis

LENGTH_SHORT_ID=10
LENGHT_TITLE_POST=200
LENGHT_DESCRIPTION_POST=1000
```

## Тесты

Локально:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Видео с проверкой

https://drive.google.com/file/d/1zHDz35VzL8XEjsgInqAHxNboMRaI8BJG/view?usp=sharing

https://drive.google.com/file/d/1eQ8wOs_CNAdEppE3XTzS38v-uoBNe12T/view?usp=sharing