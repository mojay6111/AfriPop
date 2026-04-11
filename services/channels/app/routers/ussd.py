from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.services.ussd_session import get_session, save_session, clear_session
from app.services.property_client import search_properties, format_listing_sms
from app.services.ml_client import get_valuation

router = APIRouter()

CITIES = {
    "1": "Nairobi", "2": "Mombasa", "3": "Kampala",
    "4": "Lagos",   "5": "Accra",   "6": "Dar es Salaam",
}
TYPES = {
    "1": "apartment", "2": "house",
    "3": "bedsitter", "4": "commercial",
}
BEDROOMS = {"1": 1, "2": 2, "3": 3, "4": 4}


@router.post("/ussd", response_class=PlainTextResponse)
async def ussd_handler(
    sessionId:   str           = Form(...),
    phoneNumber: str           = Form(...),
    text:        str           = Form(""),
    serviceCode: Optional[str] = Form(None),
):
    session = get_session(sessionId)
    inputs  = [t for t in text.split("*") if t] if text else []
    level   = len(inputs)

    print(f"USSD {phoneNumber} | text={text!r} | level={level} | session={session}")

    # ── LEVEL 0: Main menu ────────────────────────────────────────────────────
    if level == 0:
        save_session(sessionId, {"phone": phoneNumber, "flow": None})
        return (
            "CON Welcome to AfriProp\n"
            "1. Search property\n"
            "2. My listings\n"
            "3. Pay rent\n"
            "4. AI valuation\n"
            "5. Affordable housing\n"
            "6. Help / contact agent"
        )

    flow = inputs[0]

    # ── FLOW 1: Search property ───────────────────────────────────────────────
    if flow == "1":
        if level == 1:
            save_session(sessionId, {"phone": phoneNumber, "flow": "search"})
            return (
                "CON Select city:\n"
                "1. Nairobi\n2. Mombasa\n3. Kampala\n"
                "4. Lagos\n5. Accra\n6. Dar es Salaam"
            )
        if level == 2:
            city = CITIES.get(inputs[1], "Nairobi")
            save_session(sessionId, {
                "phone": phoneNumber, "flow": "search", "city": city
            })
            return (
                "CON Property type:\n"
                "1. Apartment\n2. House\n"
                "3. Bedsitter\n4. Commercial"
            )
        if level == 3:
            city  = CITIES.get(inputs[1], "Nairobi")
            ptype = TYPES.get(inputs[2], "apartment")
            save_session(sessionId, {
                "phone": phoneNumber, "flow": "search",
                "city": city, "type": ptype
            })
            return (
                "CON Bedrooms:\n"
                "1. 1 bedroom\n2. 2 bedrooms\n"
                "3. 3 bedrooms\n4. 4+ bedrooms"
            )
        if level == 4:
            city     = CITIES.get(inputs[1], "Nairobi")
            ptype    = TYPES.get(inputs[2], "apartment")
            bedrooms = BEDROOMS.get(inputs[3], 2)
            save_session(sessionId, {
                "phone": phoneNumber, "flow": "search",
                "city": city, "type": ptype, "bedrooms": bedrooms
            })
            return "CON Enter max budget (e.g. 50000):\n0. Skip"
        if level == 5:
            city     = CITIES.get(inputs[1], "Nairobi")
            ptype    = TYPES.get(inputs[2], "apartment")
            bedrooms = BEDROOMS.get(inputs[3], 2)
            budget   = None
            if inputs[4] != "0":
                try:
                    budget = float(inputs[4])
                except ValueError:
                    pass

            results = await search_properties(
                city=city, property_type=ptype,
                min_bedrooms=bedrooms, max_price=budget, limit=3
            )
            clear_session(sessionId)
            if not results:
                return "END No properties found.\nTry a different city or budget."
            lines = [f"AfriProp: {city} results"]
            for i, prop in enumerate(results, 1):
                lines.append(format_listing_sms(prop, i))
            lines.append("SMS sent with full details")
            return "END " + "\n".join(lines)

    # ── FLOW 2: My listings ───────────────────────────────────────────────────
    if flow == "2":
        if level == 1:
            return (
                "CON My listings:\n"
                "1. View my listings\n"
                "2. Check rent payments\n"
                "3. Report maintenance"
            )
        if level == 2 and inputs[1] == "1":
            clear_session(sessionId)
            return "END Visit afriprop.com/dashboard\nor SMS LIST to manage listings"
        if level == 2 and inputs[1] == "2":
            clear_session(sessionId)
            return "END Rent payment dashboard:\nafriprop.com/landlord/rent"
        if level == 2 and inputs[1] == "3":
            clear_session(sessionId)
            return "END Report maintenance:\nSMS: FIX [ISSUE] to AFRIPROP\nor afriprop.com/maintenance"

    # ── FLOW 3: Pay rent ──────────────────────────────────────────────────────
    if flow == "3":
        if level == 1:
            return "CON Enter property code:\n(Found on your lease agreement)"
        if level == 2:
            save_session(sessionId, {
                "phone": phoneNumber, "flow": "pay",
                "property_code": inputs[1]
            })
            return f"CON Confirm rent payment\nProperty: {inputs[1]}\nAmount will be shown\n1. Confirm\n2. Cancel"
        if level == 3:
            if inputs[2] == "1":
                clear_session(sessionId)
                return (
                    "END M-Pesa payment request sent.\n"
                    "Check your phone to complete payment.\n"
                    "You will receive SMS confirmation."
                )
            clear_session(sessionId)
            return "END Payment cancelled."

    # ── FLOW 4: AI valuation ──────────────────────────────────────────────────
    if flow == "4":
        if level == 1:
            return (
                "CON Select city:\n"
                "1. Nairobi\n2. Mombasa\n3. Kampala\n"
                "4. Lagos\n5. Accra\n6. Dar es Salaam"
            )
        if level == 2:
            return (
                "CON Bedrooms:\n"
                "1. 1BR\n2. 2BR\n3. 3BR\n4. 4BR+"
            )
        if level == 3:
            return "CON Enter floor area in sqm:\n(e.g. 80)"
        if level == 4:
            city     = CITIES.get(inputs[1], "Nairobi")
            bedrooms = BEDROOMS.get(inputs[2], 2)
            try:
                floor_area = float(inputs[3])
            except ValueError:
                floor_area = 60.0

            result = await get_valuation(
                city=city, neighbourhood=city,
                bedrooms=bedrooms, floor_area_sqm=floor_area,
            )
            clear_session(sessionId)
            if not result or result.get("estimated_value", 0) == 0:
                return "END Valuation unavailable.\nTry again later."
            value    = result.get("estimated_value", 0)
            low      = result.get("confidence_low", 0)
            high     = result.get("confidence_high", 0)
            currency = result.get("currency", "KES")
            return (
                f"END AfriProp AI Valuation\n"
                f"{bedrooms}BR in {city}:\n"
                f"Est: {currency} {value:,.0f}\n"
                f"Range: {currency} {low:,.0f}-{high:,.0f}"
            )

    # ── FLOW 5: Affordable housing ────────────────────────────────────────────
    if flow == "5":
        if level == 1:
            return (
                "CON Select city:\n"
                "1. Nairobi\n2. Mombasa\n3. Kampala\n"
                "4. Lagos\n5. Accra\n6. Dar es Salaam"
            )
        if level == 2:
            city = CITIES.get(inputs[1], "Nairobi")
            clear_session(sessionId)
            return (
                f"END Affordable housing in {city}:\n"
                "Visit: afriprop.com/affordable\n"
                "or call 0800-AFRIPROP (free)"
            )

    # ── FLOW 6: Help ──────────────────────────────────────────────────────────
    if flow == "6":
        clear_session(sessionId)
        return (
            "END AfriProp Help:\n"
            "SMS: HELP to AFRIPROP\n"
            "Web: afriprop.com\n"
            "Email: help@afriprop.com\n"
            "Agents available 8am-6pm"
        )

    clear_session(sessionId)
    return "END Invalid option. Dial *384*PROP# to start again."
