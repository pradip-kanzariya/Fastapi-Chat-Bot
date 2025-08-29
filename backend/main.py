from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.database.db import Database
from backend.routes.chat_routes import router as chat_routers
from backend.routes.user_routes import router as user_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    Database.create_engine()
    print("Database initialized at startup")
    yield
    print("Cleanup at shutdown")

app = FastAPI(lifespan=lifespan)

# Include routes
app.include_router(chat_routers)
app.include_router(user_routers)
