from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.investment import InvestmentStatus, InvestorStatus


class InvestmentPropertyOut(BaseModel):
    id:                 str
    property_id:        str
    title:              str
    description:        Optional[str]
    total_value:        float
    total_units:        int
    unit_price:         float
    currency:           str
    units_sold:         int
    units_available:    int
    minimum_investment: int
    expected_roi_pct:   float
    status:             InvestmentStatus
    created_at:         datetime

    class Config:
        from_attributes = True


class InvestmentPropertyCreate(BaseModel):
    property_id:        str
    title:              str
    description:        Optional[str] = None
    total_value:        float
    total_units:        int
    unit_price:         float
    currency:           str = "KES"
    minimum_investment: int = 1
    expected_roi_pct:   float = 12.0


class InvestRequest(BaseModel):
    investor_id:            str
    investment_property_id: str
    units:                  int
    phone:                  str
    currency:               str = "KES"


class InvestmentOut(BaseModel):
    id:                    str
    investor_id:           str
    investment_property_id:str
    units_purchased:       int
    amount_invested:       float
    currency:              str
    ownership_pct:         float
    monthly_income_share:  float
    status:                InvestorStatus
    purchased_at:          datetime

    class Config:
        from_attributes = True
