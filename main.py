from fastapi import FastAPI
from core.config import settings
from api.v1.api import api_router
# Import models to ensure they are registered with SQLAlchemy
from db import models

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to DiagnoPet Backend"}
