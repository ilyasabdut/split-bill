from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/splitbill"
    )

    class Config:
        env_file = ".env"


settings = Settings()

# Override DATABASE_URL for dev environment to use correct port
DATABASE_URL = settings.DATABASE_URL.replace("localhost:5432", "localhost:29387")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
