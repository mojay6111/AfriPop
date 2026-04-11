import requests
import base64
from datetime import datetime
from app.config import settings


def get_mpesa_token() -> str:
    credentials = base64.b64encode(
        f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    try:
        r = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {credentials}"},
            timeout=10,
        )
        return r.json().get("access_token", "")
    except Exception as e:
        print(f"M-Pesa token error: {e}")
        return ""


def get_mpesa_password() -> tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw       = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def initiate_stk_push(
    phone: str,
    amount: float,
    account_reference: str,
    description: str,
) -> dict:
    token              = get_mpesa_token()
    password, timestamp = get_mpesa_password()
    phone_clean        = phone.replace("+", "").replace("-", "").replace(" ", "")
    if phone_clean.startswith("0"):
        phone_clean = "254" + phone_clean[1:]

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password":          password,
        "Timestamp":         timestamp,
        "TransactionType":   "CustomerPayBillOnline",
        "Amount":            int(amount),
        "PartyA":            phone_clean,
        "PartyB":            settings.MPESA_SHORTCODE,
        "PhoneNumber":       phone_clean,
        "CallBackURL":       settings.MPESA_CALLBACK_URL,
        "AccountReference":  account_reference,
        "TransactionDesc":   description,
    }

    try:
        r = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
            timeout=30,
        )
        return r.json()
    except Exception as e:
        print(f"STK push error: {e}")
        return {"error": str(e)}
