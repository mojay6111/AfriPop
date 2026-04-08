import random
import string
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
import africastalking

africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
sms = africastalking.SMS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generate_otp() -> tuple[str, datetime]:
    code = "".join(random.choices(string.digits, k=6))
    expires = datetime.utcnow() + timedelta(minutes=10)
    return code, expires


def send_otp_sms(phone: str, otp: str):
    message = f"Your AfriProp verification code is {otp}. Valid for 10 minutes."
    try:
        sms.send(message, [phone])
    except Exception as e:
        print(f"SMS send failed: {e}")
