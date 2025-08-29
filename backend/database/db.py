from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from backend.models.models import Base
load_dotenv()

database_url = os.getenv("DATABASE_URL")

class Database:
    _engine = None
    _SessionLocal = None

    @classmethod
    def create_engine(cls, db_url:str=database_url):
        if cls._engine is None:
            cls._engine = create_engine(db_url)
            cls._SessionLocal = sessionmaker(bind=cls._engine, autoflush=False, autocommit=False)

            Base.metadata.create_all(bind=cls._engine)

    @classmethod
    def get_session(cls):
        if cls._SessionLocal is None:
            raise Exception("Database not initialized.")
        return cls._SessionLocal()