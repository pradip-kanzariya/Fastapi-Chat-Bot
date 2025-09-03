from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from backend.models.models import Base
from backend.configuration import settings

database_url = settings.DATABASE_URL

class InitializeDatabase:
    """Creates database connection."""
    _engine = None
    _SessionLocal = None

    @classmethod
    def create_engine(cls, db_url:str=database_url):
        """Create engine for database connection."""
        if cls._engine is None:
            cls._engine = create_engine(db_url)
            cls._SessionLocal = sessionmaker(bind=cls._engine, autoflush=False, autocommit=False)

            Base.metadata.create_all(bind=cls._engine)

    @classmethod
    def get_session(cls):
        """Returns session from created engine."""
        if cls._SessionLocal is None:
            raise Exception("Database not initialized.")
        return cls._SessionLocal()