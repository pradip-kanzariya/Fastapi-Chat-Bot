from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.schemas.user import RegisterUser
import logging
from backend.dependencies.dependencies import get_db
from backend.models.models import Users
from backend.auth.auth import hash_password, verify_password, create_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register")
async def user_register(user:RegisterUser, db:Session=Depends(get_db)):
    get_user = db.query(Users).filter(Users.user_email == user.user_email).first()

    if get_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = Users(
        username = user.username,
        user_email = user.user_email,
        user_password = hash_password(user.user_password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        get_user = db.query(Users).filter(Users.user_email == form_data.username).first()

        if not get_user or not verify_password(form_data.password, get_user.user_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        jwt_token = create_jwt_token(data=get_user)
        return {"access_token": jwt_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(e)