from fastapi import FastAPI
from backend.database.postgresql import Base, engine
from backend.routes.chat_routes import router as chat_routers

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routes
app.include_router(chat_routers)
