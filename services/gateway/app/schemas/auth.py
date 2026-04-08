from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    role: UserRole = UserRole.tenant


class UserLogin(BaseModel):
    phone: str
    password: str


class OTPVerify(BaseModel):
    phone: str
    otp_code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class UserOut(BaseModel):
    id: str
    phone: str
    email: Optional[str]
    full_name: str
    role: UserRole
    is_verified: bool

    class Config:
        from_attributes = True
