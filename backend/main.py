from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from backend.database.db import InitializeDatabase
from backend.api.routers import api_routers

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    InitializeDatabase.create_engine()
    logger.info("Database initialized at startup")
    yield
    logger.info("Cleanup at shutdown")

app = FastAPI(lifespan=lifespan)

# Include routes
app.include_router(api_routers)
