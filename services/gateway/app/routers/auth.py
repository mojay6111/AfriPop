from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, OTPVerify, TokenResponse, UserOut
from app.services.auth_service import (
    hash_password, verify_password, create_access_token,
    generate_otp, send_otp_sms
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == payload.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    otp, expires = generate_otp()
    user = User(
        full_name=payload.full_name,
        phone=payload.phone,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        otp_code=otp,
        otp_expires_at=expires,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    send_otp_sms(payload.phone, otp)
    return user


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.otp_code != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    await db.commit()
    return {"message": "Phone verified successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Phone not verified")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, user_id=user.id, role=user.role)


@router.get("/ping")
async def ping():
    return {"message": "auth router alive"}
