from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from backend.database.db import InitializeDatabase
from backend.api.routers import api_routers
from backend.middlewares.middleware import ErrorHandlingMiddleware, LogRequestMiddleware, RequestIDMiddleware, JWTAuthMiddleware
from backend.core.configuration import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    InitializeDatabase.create_engine()
    logger.info("Database initialized at startup")
    yield
    logger.info("Cleanup at shutdown")

# Fastapi app
app = FastAPI(lifespan=lifespan)

# 1. Global error handling (outermost)
app.add_middleware(ErrorHandlingMiddleware)
# 2. Request ID (so logs/errors carry IDs)
app.add_middleware(RequestIDMiddleware)
# 3. HTTPS redirect (before doing any auth or logging)
# app.add_middleware(HTTPSRedirectMiddleware)       # Run Uvicorn with SSL certificates
# 4. Authentication
app.add_middleware(JWTAuthMiddleware)
# 5. Logging (captures request, response, and status)
app.add_middleware(LogRequestMiddleware)
# 6. Built-in middlewares (like CORS, compression, etc.)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.ALLOW_ORIGINS, 
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS, 
    allow_headers=settings.ALLOW_HEADERS
)

# Include routes
app.include_router(api_routers)
