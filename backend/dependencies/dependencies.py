from backend.database.db import Database

def get_db():
    db = Database.get_session()
    try:
        yield db
    finally:
        db.close()