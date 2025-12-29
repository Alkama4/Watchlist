from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import config
from app.database import engine, Base
from app.routers import auth, titles, media

# Setup ENVs
config

# Setup DB stuff
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # allow all origins
    allow_methods=["*"],    # allow all methods
    allow_headers=["*"],    # allow all headers
    allow_credentials=True, # important to send cookies
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])
app.include_router(media.router, prefix="/media", tags=["media"])
