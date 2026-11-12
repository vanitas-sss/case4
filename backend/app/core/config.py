from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_PATH: str = "data/metrics.db"

    HEARTBEAT_INTERVAL: int = 60
    WARNING_AFTER: int = 120
    OFFLINE_AFTER: int = 150
    ALERT_AFTER_OFFLINE: int = 10
    CHECK_PERIOD: int = 30

    RETENTION_DAYS: int = Field(default=7, ge=1)
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @model_validator(mode="after")
    def validate_monitoring(self):
        if not 0 < self.WARNING_AFTER < self.OFFLINE_AFTER:
            raise ValueError("Нужно 0 < WARNING_AFTER < OFFLINE_AFTER")
        if self.CHECK_PERIOD <= 0 or self.ALERT_AFTER_OFFLINE < 0:
            raise ValueError("CHECK_PERIOD > 0, ALERT_AFTER_OFFLINE >= 0")
        return self


settings = Settings()
