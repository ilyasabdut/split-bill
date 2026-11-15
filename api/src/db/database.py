from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ilyasabdut@127.0.0.1:5432/splitbill"

    class Config:
        env_file = ".env"


settings = Settings()

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": False})
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
