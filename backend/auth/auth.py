from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import datetime
import jwt
import logging
from backend.core.configuration import settings
from fastapi.security import OAuth2PasswordBearer
from backend.models.models import Users

logger = logging.getLogger(__name__)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data, exp=None):
    """Create JWT token."""
    if exp is None:
        exp = ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.datetime.now() + datetime.timedelta(minutes=int(exp))
    payload = {
        "user_id": data.id,
        "username": data.username,
        "user_email": data.user_email,
        "exp": expire.timestamp()
    }
    try:
        payload = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
        return payload
    except Exception as e:
        logger.error(e)

def decode_jwt_token(token: str = Depends(oauth2_scheme)):
    """Decode JWT token."""
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please log in again."
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
def authenticate_user(db: Session, email: str, password: str):
    """Verify user credentials and return user object if valid."""
    try:
        user = db.query(Users).filter(Users.user_email == email).first()
        if not user or not verify_password(password, user.user_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Authenticate user faield: {e}")
        raise HTTPException(status_code=500, detail=str(e))
