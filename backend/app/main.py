from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import config
from app.database import engine, Base, AsyncSessionLocal
from app.routers import auth, titles, seasons, media, settings, user_settings, root
from app.settings.seed import init_settings
from app.services.genres import update_genres

# Setup ENVs
config

# Setup DB stuff
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await init_settings(db)
        await update_genres(db, force_update=False)

    yield

app = FastAPI(lifespan=lifespan)

origins=[
    "http://localhost:5173",
    "http://watchlist-frontend",
]

origin_regex = r"https?://192\.168\.0\.\d+(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True, # lets the browser send cookies / auth headers
)


app.include_router(root.router, prefix="", tags=["Root"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(user_settings.router, prefix="/user_settings", tags=["User Settings"])
app.include_router(titles.router, prefix="/titles", tags=["Titles"])
app.include_router(seasons.router, prefix="/seasons", tags=["Seasons"])
app.include_router(media.router, prefix="/media", tags=["Media"])
