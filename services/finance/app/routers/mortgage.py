from fastapi import APIRouter
from app.schemas.payment import MortgageRequest, MortgageResponse

router = APIRouter()


@router.post("/calculate", response_model=MortgageResponse)
async def calculate_mortgage(req: MortgageRequest):
    loan_amount    = req.property_price - req.deposit_amount
    monthly_rate   = (req.annual_interest_rate / 100) / 12
    n_payments     = req.loan_term_years * 12

    if monthly_rate == 0:
        monthly_repayment = loan_amount / n_payments
    else:
        monthly_repayment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** n_payments
        ) / ((1 + monthly_rate) ** n_payments - 1)

    total_repayment  = monthly_repayment * n_payments
    total_interest   = total_repayment - loan_amount
    affordability    = (monthly_repayment / req.monthly_income) * 100

    if affordability < 30:
        status = "comfortable"
    elif affordability < 40:
        status = "affordable"
    elif affordability < 50:
        status = "stretched"
    else:
        status = "unaffordable"

    max_repayment        = req.monthly_income * 0.35
    max_loan             = max_repayment * ((1 + monthly_rate) ** n_payments - 1) / (
        monthly_rate * (1 + monthly_rate) ** n_payments
    ) if monthly_rate > 0 else max_repayment * n_payments
    max_affordable_price = max_loan + req.deposit_amount

    return MortgageResponse(
        loan_amount=round(loan_amount, 2),
        monthly_repayment=round(monthly_repayment, 2),
        total_repayment=round(total_repayment, 2),
        total_interest=round(total_interest, 2),
        affordability_ratio=round(affordability, 2),
        affordability_status=status,
        max_affordable_price=round(max_affordable_price, 2),
        currency=req.currency,
    )
