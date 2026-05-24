import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

db_host = os.environ.get("DB_HOST", 'localhost')
db_port = os.environ.get("DB_PORT", '5432')
db_name = os.environ.get("DB_NAME", 'watchlist')
db_user = os.environ.get("DB_USER", 'postgres')
db_pass = os.environ.get("DB_PASSWORD", 'postgres')

database_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

engine = create_async_engine(database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

Base = declarative_base()
