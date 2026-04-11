import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Enum as SAEnum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class InvestmentStatus(str, enum.Enum):
    open   = "open"
    funded = "funded"
    closed = "closed"


class InvestorStatus(str, enum.Enum):
    active  = "active"
    exited  = "exited"


class InvestmentProperty(Base):
    __tablename__ = "investment_properties"

    id: Mapped[str] = mapped_column(String, primary_key=True,
                                    default=lambda: str(uuid.uuid4()))
    property_id:        Mapped[str]   = mapped_column(String, nullable=False)
    title:              Mapped[str]   = mapped_column(String, nullable=False)
    description:        Mapped[str]   = mapped_column(Text, nullable=True)
    total_value:        Mapped[float] = mapped_column(Float, nullable=False)
    total_units:        Mapped[int]   = mapped_column(Integer, nullable=False)
    unit_price:         Mapped[float] = mapped_column(Float, nullable=False)
    currency:           Mapped[str]   = mapped_column(String(10), default="KES")
    units_sold:         Mapped[int]   = mapped_column(Integer, default=0)
    units_available:    Mapped[int]   = mapped_column(Integer, nullable=False)
    minimum_investment: Mapped[int]   = mapped_column(Integer, default=1)
    expected_roi_pct:   Mapped[float] = mapped_column(Float, default=12.0)
    status: Mapped[InvestmentStatus] = mapped_column(
        SAEnum(InvestmentStatus), default=InvestmentStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                  onupdate=datetime.utcnow)


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[str] = mapped_column(String, primary_key=True,
                                    default=lambda: str(uuid.uuid4()))
    investor_id:             Mapped[str]   = mapped_column(String, nullable=False, index=True)
    investment_property_id:  Mapped[str]   = mapped_column(String, nullable=False, index=True)
    units_purchased:         Mapped[int]   = mapped_column(Integer, nullable=False)
    amount_invested:         Mapped[float] = mapped_column(Float, nullable=False)
    currency:                Mapped[str]   = mapped_column(String(10), default="KES")
    ownership_pct:           Mapped[float] = mapped_column(Float, nullable=False)
    monthly_income_share:    Mapped[float] = mapped_column(Float, default=0.0)
    payment_id:              Mapped[str]   = mapped_column(String, nullable=True)
    status: Mapped[InvestorStatus] = mapped_column(
        SAEnum(InvestorStatus), default=InvestorStatus.active
    )
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
