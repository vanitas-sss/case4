from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_PATH: str = "data/metrics.db"
    AGENT_TOKEN: str = ""

    HEARTBEAT_INTERVAL: int = 60
    WARNING_AFTER: int = 120
    OFFLINE_AFTER: int = 150
    ALERT_AFTER_OFFLINE: int = 10
    CHECK_PERIOD: int = 30

    RETENTION_DAYS: int = 7


settings = Settings()
