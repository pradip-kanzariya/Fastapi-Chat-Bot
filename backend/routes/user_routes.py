from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.schemas.user import RegisterUser, LoginUser
from backend.dependencies.dependencies import get_db
from backend.models.models import Users

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register")
async def user_register(user:RegisterUser, db:Session=Depends(get_db)):
    get_user = db.query(Users).filter(Users.user_email == user.user_email).first()

    if get_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = Users(
        username = user.username,
        user_email = user.user_email,
        user_password = user.user_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def user_login(user:LoginUser, db:Session=Depends(get_db)):
    get_user = db.query(Users).filter(Users.user_email == user.user_email).first()

    if not get_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if get_user.user_email == user.user_email and get_user.user_password == user.user_password:
        return get_user
    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")