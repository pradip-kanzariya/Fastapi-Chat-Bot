from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
from backend.schemas.user_schema import RegisterUser
from backend.dependencies.dependencies import get_db
from backend.auth.auth import create_jwt_token, authenticate_user
from backend.api.crud.user_crud import register_new_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register")
async def user_register(user: RegisterUser, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        new_user = register_new_user(db, user)
        return {"id": new_user.id, "email": new_user.user_email}
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        return HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        jwt_token = create_jwt_token(data=user)
        return {"access_token": jwt_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return HTTPException(status_code=500, detail=str(e))
