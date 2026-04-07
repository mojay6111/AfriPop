from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/at/sms")
async def at_sms_webhook(request: Request):
    body = await request.json()
    return {"status": "received", "data": body}


@router.post("/at/ussd")
async def at_ussd_webhook(request: Request):
    body = await request.form()
    return {"status": "received"}
