from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import config
from app.database import engine, Base
from app.routers import auth, titles

# Setup ENVs
config

# Setup DB stuff
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])
