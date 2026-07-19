# config/postgres_config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import asyncpg

class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_")
    host: str = "192.168.15.201"
    port: int = 5432
    database: str = "smartfinance"
    user: str = "smartfinance"
    password: str  = "sgt"                    # sem default: falha no boot se PG_PASSWORD faltar
    min_size: int = 2
    max_size: int = 10

@lru_cache
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings()

async def create_pg_pool() -> asyncpg.Pool:
    s = get_postgres_settings()
    return await asyncpg.create_pool(
        host=s.host, port=s.port, database=s.database,
        user=s.user, password=s.password,
        min_size=s.min_size, max_size=s.max_size,
        command_timeout=30,
    )