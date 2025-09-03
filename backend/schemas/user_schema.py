from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    """Schema for route register user."""
    username: str
    user_email: EmailStr
    user_password: str