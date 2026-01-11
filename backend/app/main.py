from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import config
from app.database import engine, Base, AsyncSessionLocal
from app.routers import auth, titles, media, settings, user_settings, root
from app.settings.seed import init_settings

# Setup ENVs
config

# Setup DB stuff
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await init_settings(db)

    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # allow all origins
    allow_methods=["*"],    # allow all methods
    allow_headers=["*"],    # allow all headers
    allow_credentials=True, # important to send cookies
)


app.include_router(root.router, prefix="", tags=["Root"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(user_settings.router, prefix="/user_settings", tags=["User Settings"])
app.include_router(titles.router, prefix="/titles", tags=["Titles"])
app.include_router(media.router, prefix="/media", tags=["Media"])
