from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models.payment import Payment, RentLedger, PaymentStatus, LedgerStatus, PaymentMethod
from app.schemas.payment import MpesaInitiateRequest, PaymentOut, LedgerOut, LedgerCreateRequest
from app.services.mpesa import initiate_stk_push
import uuid

router = APIRouter()


@router.post("/mpesa/initiate")
async def mpesa_initiate(
    req: MpesaInitiateRequest,
    db: AsyncSession = Depends(get_db),
):
    ref = f"AFRIPROP-{uuid.uuid4().hex[:8].upper()}"

    payment = Payment(
        tenant_id=req.tenant_id,
        landlord_id=req.landlord_id,
        property_id=req.property_id,
        amount=req.amount,
        currency=req.currency,
        payment_method=PaymentMethod.mpesa,
        status=PaymentStatus.pending,
        reference_code=ref,
        description=req.description,
    )
    db.add(payment)
    await db.flush()

    result = initiate_stk_push(
        phone=req.phone,
        amount=req.amount,
        account_reference=ref,
        description=req.description,
    )

    if "CheckoutRequestID" in result:
        payment.mpesa_checkout_request_id = result["CheckoutRequestID"]
        await db.commit()
        return {
            "status":              "pending",
            "payment_id":          payment.id,
            "checkout_request_id": result["CheckoutRequestID"],
            "customer_message":    result.get("CustomerMessage", "Check your phone"),
            "reference":           ref,
        }
    else:
        payment.status = PaymentStatus.failed
        payment.failure_reason = str(result)
        await db.commit()
        return {
            "status":  "failed",
            "error":   result,
            "message": "STK push failed. Check M-Pesa credentials.",
        }


@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    print(f"M-Pesa callback received: {body}")

    try:
        callback  = body["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        checkout_id = callback["CheckoutRequestID"]

        result = await db.execute(
            select(Payment).where(
                Payment.mpesa_checkout_request_id == checkout_id
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return {"ResultCode": 0, "ResultDesc": "Accepted"}

        if result_code == 0:
            metadata = {
                item["Name"]: item.get("Value")
                for item in callback["CallbackMetadata"]["Item"]
            }
            payment.status               = PaymentStatus.completed
            payment.mpesa_receipt_number = str(metadata.get("MpesaReceiptNumber", ""))
            payment.paid_at              = datetime.utcnow()

            ledger_result = await db.execute(
                select(RentLedger).where(
                    RentLedger.property_id == payment.property_id,
                    RentLedger.tenant_id   == payment.tenant_id,
                    RentLedger.status      != LedgerStatus.paid,
                )
            )
            ledger = ledger_result.scalars().first()
            if ledger:
                ledger.amount_paid += payment.amount
                ledger.balance      = ledger.amount_due - ledger.amount_paid
                ledger.payment_id   = payment.id
                ledger.status = (
                    LedgerStatus.paid if ledger.balance <= 0
                    else LedgerStatus.partial
                )
        else:
            payment.status         = PaymentStatus.failed
            payment.failure_reason = callback.get("ResultDesc", "Failed")

        await db.commit()
    except Exception as e:
        print(f"Callback processing error: {e}")

    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.get("/history/{tenant_id}", response_model=list[PaymentOut])
async def payment_history(tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Payment)
        .where(Payment.tenant_id == tenant_id)
        .order_by(Payment.created_at.desc())
    )
    return result.scalars().all()


@router.post("/ledger", response_model=LedgerOut)
async def create_ledger_entry(
    req: LedgerCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entry = RentLedger(
        tenant_id=req.tenant_id,
        landlord_id=req.landlord_id,
        property_id=req.property_id,
        month_year=req.month_year,
        due_date=req.due_date,
        amount_due=req.amount_due,
        amount_paid=0.0,
        balance=req.amount_due,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/ledger/{property_id}", response_model=list[LedgerOut])
async def get_ledger(property_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RentLedger)
        .where(RentLedger.property_id == property_id)
        .order_by(RentLedger.due_date.desc())
    )
    return result.scalars().all()
