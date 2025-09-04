from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
from backend.auth.auth import hash_password
from backend.schemas.user_schema import RegisterUser
from backend.models.models import Users

logger = logging.getLogger(__name__)

def register_new_user(db: Session, user: RegisterUser):
    """Create a new user if email does not already exist."""
    try:
        existing_user = db.query(Users).filter(Users.user_email == user.user_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = Users(
            username=user.username,
            user_email=user.user_email,
            user_password=hash_password(user.user_password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        logger.error(f"Register new user failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))