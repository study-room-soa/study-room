from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()

app = FastAPI(
    title="Booking Service",
    description="Microservice for managing room reservations.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)