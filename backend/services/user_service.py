from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.models import Users
from backend.auth.auth import hash_password, verify_password
from backend.schemas.user_schema import RegisterUser


async def register_new_user(db: Session, user: RegisterUser):
    """Create a new user if email does not already exist."""
    existing_user = db.query(Users).filter(Users.user_email == user.user_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = Users(
        username=user.username,
        user_email=user.user_email,
        user_password=await hash_password(user.user_password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def authenticate_user(db: Session, email: str, password: str):
    """Verify user credentials and return user object if valid."""
    user = db.query(Users).filter(Users.user_email == email).first()
    if not user or not await verify_password(password, user.user_password):
        return None
    return user
