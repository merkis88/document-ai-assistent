from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    BOT_TOKEN: str | None = None

    WEBHOOK_BASE_URL: str = ""
    WEBHOOK_PATH: str = "/telegram/webhook"
    WEBHOOK_SECRET: str = ""

    WEB_SERVER_HOST: str = "127.0.0.1"
    WEB_SERVER_PORT: int = 8080

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )



settings = Settings()