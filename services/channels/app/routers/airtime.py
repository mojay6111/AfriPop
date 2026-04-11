from fastapi import APIRouter
from pydantic import BaseModel
from app.services.at_client import send_airtime

router = APIRouter()

CURRENCY_MAP = {
    "+254": "KES", "+256": "UGX",
    "+234": "NGN", "+233": "GHS", "+255": "TZS",
}

REWARDS = {
    "profile_verified":     {"amount": 20,  "currency": "KES"},
    "review_submitted":     {"amount": 10,  "currency": "KES"},
    "agent_3_transactions": {"amount": 50,  "currency": "KES"},
    "first_ussd_search":    {"amount": 5,   "currency": "KES"},
}


class AirtimeRewardRequest(BaseModel):
    phone:      str
    reason:     str
    currency:   str = "KES"


@router.post("/airtime/reward")
async def disburse_reward(req: AirtimeRewardRequest):
    reward = REWARDS.get(req.reason)
    if not reward:
        return {"status": "error", "message": f"Unknown reward reason: {req.reason}"}

    result = send_airtime(
        phone=req.phone,
        currency=req.currency or reward["currency"],
        amount=reward["amount"],
    )

    print(f"Airtime reward: {req.phone} | {req.reason} | "
          f"{reward['currency']} {reward['amount']} | {result['status']}")

    return {
        "status":   result["status"],
        "phone":    req.phone,
        "reason":   req.reason,
        "amount":   reward["amount"],
        "currency": reward["currency"],
    }
