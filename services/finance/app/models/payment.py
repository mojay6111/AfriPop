import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Enum as SAEnum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    mpesa   = "mpesa"
    mtn     = "mtn"
    airtel  = "airtel"
    card    = "card"
    cash    = "cash"


class PaymentStatus(str, enum.Enum):
    pending   = "pending"
    completed = "completed"
    failed    = "failed"
    refunded  = "refunded"


class LedgerStatus(str, enum.Enum):
    pending  = "pending"
    paid     = "paid"
    partial  = "partial"
    overdue  = "overdue"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True,
                                    default=lambda: str(uuid.uuid4()))
    tenant_id:   Mapped[str] = mapped_column(String, nullable=False, index=True)
    landlord_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    property_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    amount:      Mapped[float] = mapped_column(Float, nullable=False)
    currency:    Mapped[str]   = mapped_column(String(10), default="KES")
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod), default=PaymentMethod.mpesa
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), default=PaymentStatus.pending
    )
    mpesa_checkout_request_id: Mapped[str] = mapped_column(String, nullable=True)
    mpesa_receipt_number:      Mapped[str] = mapped_column(String, nullable=True)
    reference_code:  Mapped[str]  = mapped_column(String, nullable=True)
    description:     Mapped[str]  = mapped_column(Text, nullable=True)
    failure_reason:  Mapped[str]  = mapped_column(String, nullable=True)
    paid_at:         Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at:      Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:      Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                       onupdate=datetime.utcnow)


class RentLedger(Base):
    __tablename__ = "rent_ledger"

    id: Mapped[str] = mapped_column(String, primary_key=True,
                                    default=lambda: str(uuid.uuid4()))
    tenant_id:   Mapped[str]   = mapped_column(String, nullable=False, index=True)
    landlord_id: Mapped[str]   = mapped_column(String, nullable=False)
    property_id: Mapped[str]   = mapped_column(String, nullable=False, index=True)
    month_year:  Mapped[str]   = mapped_column(String(7), nullable=False)
    due_date:    Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount_due:  Mapped[float] = mapped_column(Float, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    balance:     Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[LedgerStatus] = mapped_column(
        SAEnum(LedgerStatus), default=LedgerStatus.pending
    )
    payment_id:  Mapped[str]  = mapped_column(String, nullable=True)
    notes:       Mapped[str]  = mapped_column(Text, nullable=True)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                   onupdate=datetime.utcnow)
