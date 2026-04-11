from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.investment import InvestmentProperty, Investment, InvestmentStatus
from app.schemas.investment import (
    InvestmentPropertyOut, InvestmentPropertyCreate,
    InvestRequest, InvestmentOut
)

router = APIRouter()


@router.get("/", response_model=list[InvestmentPropertyOut])
async def list_investment_properties(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InvestmentProperty)
        .where(InvestmentProperty.status == InvestmentStatus.open)
        .order_by(InvestmentProperty.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=InvestmentPropertyOut, status_code=201)
async def create_investment_property(
    payload: InvestmentPropertyCreate,
    db: AsyncSession = Depends(get_db),
):
    inv_prop = InvestmentProperty(
        property_id=payload.property_id,
        title=payload.title,
        description=payload.description,
        total_value=payload.total_value,
        total_units=payload.total_units,
        unit_price=payload.unit_price,
        currency=payload.currency,
        units_available=payload.total_units,
        minimum_investment=payload.minimum_investment,
        expected_roi_pct=payload.expected_roi_pct,
    )
    db.add(inv_prop)
    await db.commit()
    await db.refresh(inv_prop)
    return inv_prop


@router.post("/invest", response_model=InvestmentOut, status_code=201)
async def invest(req: InvestRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InvestmentProperty).where(
            InvestmentProperty.id == req.investment_property_id
        )
    )
    inv_prop = result.scalar_one_or_none()
    if not inv_prop:
        raise HTTPException(status_code=404, detail="Investment property not found")
    if inv_prop.units_available < req.units:
        raise HTTPException(
            status_code=400,
            detail=f"Only {inv_prop.units_available} units available"
        )

    amount        = req.units * inv_prop.unit_price
    ownership_pct = (req.units / inv_prop.total_units) * 100
    monthly_share = (ownership_pct / 100) * (
        inv_prop.total_value * (inv_prop.expected_roi_pct / 100) / 12
    )

    investment = Investment(
        investor_id=req.investor_id,
        investment_property_id=req.investment_property_id,
        units_purchased=req.units,
        amount_invested=amount,
        currency=req.currency,
        ownership_pct=round(ownership_pct, 4),
        monthly_income_share=round(monthly_share, 2),
    )

    inv_prop.units_sold      += req.units
    inv_prop.units_available -= req.units
    if inv_prop.units_available == 0:
        inv_prop.status = InvestmentStatus.funded

    db.add(investment)
    await db.commit()
    await db.refresh(investment)
    return investment


@router.get("/portfolio/{investor_id}", response_model=list[InvestmentOut])
async def investor_portfolio(investor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Investment)
        .where(Investment.investor_id == investor_id)
        .order_by(Investment.purchased_at.desc())
    )
    return result.scalars().all()
