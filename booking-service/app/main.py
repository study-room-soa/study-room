from fastapi import FastAPI

app = FastAPI(
    title="Booking Service",
    description="Microservice for managing room reservations.",
    version="1.0.0"
)