import sys
from pathlib import Path
from typing import Any

import dotenv
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings

from Shared.Singleton import Singleton

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

config_app = dotenv.dotenv_values(env_path)


class ProjectSettings(BaseModel):
    length_short_id: int
    length_title: int
    length_description: int


    @field_validator('length_short_id', 'length_title', 'length_description')
    @classmethod
    def length_check(cls, value: Any, info: ValidationInfo) -> int:
        try:
            length = int(value)
        except (ValueError, TypeError):
            raise Exception(f"{info.field_name} must be int")

        min_val, max_val = None, None
        if info.field_name == "length_short_id":
            min_val, max_val = 5, 100

            if length < min_val or length > max_val:
                raise Exception(f"{info.field_name} must be > {min_val} and < {max_val}")

        elif info.field_name == "length_title":
            min_val, max_val = 0, 200

        else:
            min_val, max_val = 0, 1000

        if length <= min_val or length > max_val:
            raise Exception(f"{info.field_name} must be > {min_val} and < {max_val}")

        return length



class DbSettings(BaseModel):
    drivername: str = config_app.get("DB_DRIVER", "postgresql+asyncpg")
    username: str = config_app.get("DB_USER", "postgres")
    password: str = config_app.get("DB_PASSWORD", "postgres")
    host: str = config_app.get("DB_HOST", "localhost")
    port: int = int(config_app.get("DB_PORT", 5432))
    database: str = config_app.get("DB_NAME", "effective_mobile")
    url: str = config_app.get(
        "DB_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/effective_mobile",
    )


class RedisSettings(BaseModel):
    password: str = config_app.get("REDIS_PASSWORD", "redis")
    user: str = config_app.get("REDIS_USER", "redis")
    user_password: str = config_app.get("REDIS_USER_PASSWORD", "redis")
    connect_path: str = config_app.get("REDIS_PATH")
    db: int = config_app.get("REDIS_DB")


class Settings(BaseSettings):
    api_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    redis: RedisSettings = RedisSettings()

    project: ProjectSettings = ProjectSettings(
        length_short_id=config_app.get("LENGTH_SHORT_ID", 5),
        length_title=config_app.get("LENGHT_TITLE_POST", 200),
        length_description=config_app.get("LENGHT_DESCRIPTION_POST", 1000)
    )
