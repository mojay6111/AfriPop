from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.payment import PaymentMethod, PaymentStatus, LedgerStatus


class MpesaInitiateRequest(BaseModel):
    phone:       str
    amount:      float
    property_id: str
    tenant_id:   str
    landlord_id: str
    description: str = "Rent payment"
    currency:    str = "KES"


class MpesaInitiateResponse(BaseModel):
    checkout_request_id: str
    merchant_request_id: str
    response_code:       str
    customer_message:    str


class PaymentOut(BaseModel):
    id:             str
    tenant_id:      str
    property_id:    str
    amount:         float
    currency:       str
    payment_method: PaymentMethod
    status:         PaymentStatus
    reference_code: Optional[str]
    description:    Optional[str]
    paid_at:        Optional[datetime]
    created_at:     datetime

    class Config:
        from_attributes = True


class LedgerOut(BaseModel):
    id:          str
    tenant_id:   str
    property_id: str
    month_year:  str
    due_date:    datetime
    amount_due:  float
    amount_paid: float
    balance:     float
    status:      LedgerStatus
    payment_id:  Optional[str]
    created_at:  datetime

    class Config:
        from_attributes = True


class LedgerCreateRequest(BaseModel):
    tenant_id:   str
    landlord_id: str
    property_id: str
    month_year:  str
    due_date:    datetime
    amount_due:  float


class MortgageRequest(BaseModel):
    property_price:      float
    deposit_amount:      float
    loan_term_years:     int
    annual_interest_rate:float
    monthly_income:      float
    currency:            str = "KES"


class MortgageResponse(BaseModel):
    loan_amount:          float
    monthly_repayment:    float
    total_repayment:      float
    total_interest:       float
    affordability_ratio:  float
    affordability_status: str
    max_affordable_price: float
    currency:             str
