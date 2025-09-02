from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
import datetime
import jwt
import logging
from backend.configuration import settings
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data, exp=None):
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
