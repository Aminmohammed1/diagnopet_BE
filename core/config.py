from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DiagnoPet Backend"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@host:port/dbname"

    class Config:
        env_file = ".env"

settings = Settings()
