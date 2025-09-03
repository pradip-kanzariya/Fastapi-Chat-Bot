from backend.database.db import InitializeDatabase

def get_db():
    """Returns db yield from database connection."""
    db = InitializeDatabase.get_session()
    try:
        yield db
    finally:
        db.close()