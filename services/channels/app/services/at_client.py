import africastalking
from app.config import settings

africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)

_sms     = africastalking.SMS
_airtime = africastalking.Airtime


def send_sms(phone: str, message: str) -> dict:
    try:
        response = _sms.send(message, [phone])
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"SMS send failed to {phone}: {e}")
        return {"status": "failed", "error": str(e)}


def send_sms_bulk(phones: list, message: str) -> dict:
    try:
        response = _sms.send(message, phones)
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"Bulk SMS send failed: {e}")
        return {"status": "failed", "error": str(e)}


def send_airtime(phone: str, currency: str, amount: float) -> dict:
    try:
        response = _airtime.send(
            phone_number=phone,
            currency_code=currency,
            amount=amount
        )
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"Airtime send failed to {phone}: {e}")
        return {"status": "failed", "error": str(e)}
