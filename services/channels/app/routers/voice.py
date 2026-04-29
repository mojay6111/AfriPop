from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.services.property_client import search_properties

router = APIRouter()


def xml_response(content: str) -> PlainTextResponse:
    return PlainTextResponse(
        content=f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n{content}\n</Response>",
        media_type="application/xml"
    )


@router.post("/voice/inbound", response_class=PlainTextResponse)
async def voice_inbound(
    isActive:    Optional[str] = Form(None),
    callerNumber:Optional[str] = Form(None),
    dtmfDigits:  Optional[str] = Form(None),
    sessionId:   Optional[str] = Form(None),
):
    print(f"Voice call: {callerNumber} | digit={dtmfDigits} | active={isActive}")

    if isActive == "0":
        return xml_response("<Say>Thank you for calling AfriProp. Goodbye.</Say>")

    # First contact — no digit yet
    if not dtmfDigits:
        return xml_response(
            "<GetDigits timeout=\"30\" finishOnKey=\"#\" callbackUrl=\"/api/v1/channels/voice/inbound\">"
            "<Say>Welcome to AfriProp. Africa's property intelligence platform. "
            "Press 1 for property listings in your city. "
            "Press 2 for an AI property valuation. "
            "Press 3 to speak to an agent. "
            "Press 0 to end this call.</Say>"
            "</GetDigits>"
        )

    digit = dtmfDigits.strip()

    if digit == "1":
        # Detect city from caller number prefix
        city = "Nairobi"
        if callerNumber:
            if callerNumber.startswith("+234") or callerNumber.startswith("234"):
                city = "Lagos"
            elif callerNumber.startswith("+233") or callerNumber.startswith("233"):
                city = "Accra"
            elif callerNumber.startswith("+256") or callerNumber.startswith("256"):
                city = "Kampala"
            elif callerNumber.startswith("+255") or callerNumber.startswith("255"):
                city = "Dar es Salaam"

        results = await search_properties(city=city, limit=3)

        if not results:
            return xml_response(
                f"<Say>No properties currently available in {city}. "
                "Please visit afriprop dot com or send an SMS with your search. Goodbye.</Say>"
            )

        speech_parts = [f"Here are the top listings in {city}."]
        for i, prop in enumerate(results, 1):
            bedrooms  = prop.get("bedrooms", 0)
            prop_type = prop.get("property_type", "property")
            nb        = prop.get("neighbourhood", "")
            price     = prop.get("price", 0)
            currency  = prop.get("currency", "KES")
            period    = prop.get("price_period", "monthly")
            period_label = {"monthly":"month","yearly":"year","once":"sale"}.get(period, period)
            speech_parts.append(
                f"Listing {i}. {bedrooms} bedroom {prop_type} in {nb}. "
                f"{currency} {price:,.0f} per {period_label}."
            )

        speech_parts.append(
            "Press 1 to hear these again. "
            "Press 2 to receive SMS with full details. "
            "Press 0 to end."
        )

        speech = " ".join(speech_parts)
        return xml_response(
            f"<GetDigits timeout=\"15\" finishOnKey=\"#\" "
            f"callbackUrl=\"/api/v1/channels/voice/inbound\">"
            f"<Say>{speech}</Say>"
            f"</GetDigits>"
        )

    if digit == "2":
        return xml_response(
            "<Say>For an AI property valuation, please send an SMS with "
            "V A L E followed by your bedroom count, neighbourhood, and floor area. "
            "For example: V A L E 2 B R Westlands 80 S Q M. Goodbye.</Say>"
        )

    if digit == "3":
        return xml_response(
            "<Say>Connecting you to an AfriProp agent. Please hold.</Say>"
            "<Dial phoneNumbers=\"+254700000000\"/>"
        )

    if digit == "0":
        return xml_response(
            "<Say>Thank you for calling AfriProp. Visit afriprop dot com. Goodbye.</Say>"
        )

    return xml_response(
        "<Say>Invalid option. Please dial again and select 1, 2, or 3.</Say>"
    )
