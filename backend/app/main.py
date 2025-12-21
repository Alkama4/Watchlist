from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import config
from app.database import engine, Base
from app.routers import auth

# Setup ENVs
config

# Setup DB stuff
@asynccontextmanager
async def lifespan():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
