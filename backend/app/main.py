from fastapi import FastAPI
import app.config
from app.database import engine, Base
from app.routers import auth

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
