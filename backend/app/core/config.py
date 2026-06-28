from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bqadmin:bqsecret123@localhost:5432/bq_attendance"
    SECRET_KEY: str = "supersecretkey_change_in_production_123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    STORAGE_PATH: str = "./storage"
    CORS_ORIGINS: str = "http://localhost:3000"
    APP_NAME: str = "Bano Qabil Attendance System"
    ORG_CODE: str = "BQ"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
