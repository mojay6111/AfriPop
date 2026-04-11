from fastapi import APIRouter, Form
from typing import Optional
from app.services.sms_parser import parse_sms, format_help_sms
from app.services.property_client import search_properties, format_listing_sms
from app.services.ml_client import get_valuation, format_valuation_sms
from app.services.at_client import send_sms

router = APIRouter()


@router.post("/sms/inbound")
async def sms_inbound(
    From: str     = Form(..., alias="from"),
    To:   str     = Form(..., alias="to"),
    text: str     = Form(...),
    date: Optional[str] = Form(None),
):
    phone   = From
    message = text.strip()
    parsed  = parse_sms(message)
    command = parsed.get("command")

    print(f"SMS from {phone}: {message} → {parsed}")

    if command == "HELP":
        response = format_help_sms()

    elif command == "SEARCH":
        results = await search_properties(
            city=parsed.get("city"),
            property_type=parsed.get("property_type"),
            min_bedrooms=parsed.get("bedrooms"),
            max_price=parsed.get("max_price"),
            limit=3,
        )
        if not results:
            response = (
                "No properties found matching your search.\n"
                "Try: SEARCH 2BR NAIROBI or HOUSE 3BR LAGOS"
            )
        else:
            lines = ["AfriProp Results:"]
            for i, prop in enumerate(results, 1):
                lines.append(format_listing_sms(prop, i))
            lines.append("Reply with ID for details")
            response = "\n".join(lines)

    elif command == "VALE":
        city         = parsed.get("city", "Nairobi")
        neighbourhood = parsed.get("neighbourhood", "Westlands")
        bedrooms     = parsed.get("bedrooms", 2)
        floor_area   = parsed.get("floor_area", 60.0)

        result   = await get_valuation(
            city=city, neighbourhood=neighbourhood,
            bedrooms=bedrooms, floor_area_sqm=floor_area,
        )
        response = format_valuation_sms(result, city, bedrooms)

    elif command == "LIST":
        response = (
            "To list your property, visit:\n"
            "afriprop.com/list\n"
            "Or dial *384*PROP# and select option 2"
        )

    elif command == "RENT":
        response = (
            "Rent payment status:\n"
            "Dial *384*PROP# and select option 3\n"
            "or visit afriprop.com/pay"
        )

    else:
        response = format_help_sms()

    send_sms(phone, response)
    return {"status": "ok", "response_sent": response}
