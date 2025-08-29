from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    username: str
    user_email: EmailStr
    user_password: str

class LoginUser(BaseModel):
    user_email: EmailStr
    user_password: str