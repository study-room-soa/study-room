from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from .database import Base, engine
from . import models
from .routes import router
from .clients import client

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        client.close()
        engine.dispose()

app = FastAPI(
    title="Room Service",
    description="Microservice for managing buildings and rooms.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.exception_handler(HTTPException)
async def custom_exception_handler(
    request: Request,
    exc: HTTPException
):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"error": exc.detail},
            headers={"WWW-Authenticate": "Bearer"}
        )
    return await http_exception_handler(request, exc)