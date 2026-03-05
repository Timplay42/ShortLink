# Effective Mobile Test Task

Бэкенд-приложение на **FastAPI** с:
- JWT-аутентификацией (access + refresh cookies),
- ролевой моделью доступа (RBAC),
- административными и пользовательскими действиями,
- Jinja UI для базовых пользовательских сценариев.

## Комментарий по ТЗ

Вместо email в качестве логина используется `username`.  
На функциональность это не влияет: авторизация, роли и доступы работают корректно.

## Что реализовано

- Регистрация и вход пользователя.
- Выход из аккаунта.
- Обновление и деактивация своего аккаунта.
- Разграничение прав:
  - обычный пользователь,
  - администратор.
- Назначение ролей (админ-функционал).
- Автосоздание ролей/permission и bootstrap admin-пользователя при старте.
- Миграции Alembic.
- Jinja страницы:
  - login,
  - register,
  - profile,
  - admin panel.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Alembic
- Jinja2
- Docker / Docker Compose

## Запуск (Docker)

Из корня проекта:

```bash
docker-compose up -d
```

Если внешняя сеть `backend_network` ещё не создана:

```bash
docker network create backend_network
```

## Доступные URL

- Сервер: [http://0.0.0.0:8010](http://0.0.0.0:8010)
- Swagger: [http://0.0.0.0:8010/api/docs/](http://0.0.0.0:8010/api/docs/)
- Jinja UI: [http://0.0.0.0:8010/](http://0.0.0.0:8010/)  
  (редирект на [http://0.0.0.0:8010/api/v1/auth/](http://0.0.0.0:8010/api/v1/auth/))

## Что происходит при старте контейнера

`entrypoint.sh` выполняет:
1. Ожидание доступности БД.
2. `alembic upgrade head`.
3. Bootstrap прав/ролей и admin-пользователя (если отсутствует).
4. Запуск приложения.

## Переменные окружения

Основные параметры в `.env`:
- `DB_*` — настройки БД
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `DB_WAIT_MAX_ATTEMPTS`
- `DB_WAIT_SLEEP_SECONDS`

Для bootstrap admin (опционально):
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_NAME`
- `ADMIN_LASTNAME`
- `ADMIN_DESCRIPTION`
