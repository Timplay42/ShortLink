from pathlib import Path

import dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

config_app = dotenv.dotenv_values(env_path)


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = config_app.get("ALGORITHM", "RS256")
    access_token_expire_minutes: int = int(config_app.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    refresh_token_expire_days: int = int(config_app.get("REFRESH_TOKEN_EXPIRE_DAYS", 30))


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


class Settings(BaseSettings):
    api_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    auth_jwt: AuthJWT = AuthJWT()
