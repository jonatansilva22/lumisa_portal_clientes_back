from pydantic_settings import BaseSettings

from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int

    CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list[str]:
        value = self.CORS_ORIGINS
        if value is None:
            return []
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                try:
                    import json
                    return json.loads(value)
                except Exception:
                    return []
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return []

    class Config:
        env_file = ".env"

settings = Settings()