from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_PATH: str = "data/metrics.db"

    HEARTBEAT_INTERVAL: int = 5
    WARNING_AFTER: int = 10
    OFFLINE_AFTER: int = 20
    ALERT_AFTER_OFFLINE: int = 10
    CHECK_PERIOD: int = 5

    RETENTION_DAYS: int = 7


settings = Settings()
