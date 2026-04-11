CITY_ALIASES = {
    "nairobi": "Nairobi", "nbi": "Nairobi",
    "mombasa": "Mombasa", "msa": "Mombasa",
    "kampala": "Kampala", "kla": "Kampala",
    "lagos":   "Lagos",   "lag": "Lagos",
    "accra":   "Accra",   "acc": "Accra",
    "dar":     "Dar es Salaam", "dares": "Dar es Salaam",
}

TYPE_ALIASES = {
    "apartment": "apartment", "apt":       "apartment",
    "house":     "house",     "bungalow":  "house",
    "land":      "land",      "plot":      "land",
    "bedsitter": "bedsitter", "bedsit":    "bedsitter", "bed":  "bedsitter",
    "commercial": "commercial","office":   "commercial", "shop": "commercial",
}

COMMANDS = {
    "HELP", "LIST", "RENT", "VALE", "SEARCH",
    "HOUSE", "APARTMENT", "LAND", "BEDSITTER",
}


def parse_sms(text: str) -> dict:
    text   = text.strip().upper()
    tokens = text.split()

    if not tokens:
        return {"command": "HELP"}

    command = tokens[0]

    # HELP command
    if command == "HELP":
        return {"command": "HELP"}

    # LIST command — landlord listing submission
    if command == "LIST":
        return {"command": "LIST"}

    # RENT command — check payment status
    if command in ("RENT", "RENT DUE"):
        return {"command": "RENT"}

    # VALE command — AI valuation
    # Format: VALE 3BR WESTLANDS 120SQM
    if command == "VALE":
        result = {"command": "VALE", "bedrooms": 2,
                  "neighbourhood": None, "floor_area": 60.0}
        for token in tokens[1:]:
            if "BR" in token:
                try:
                    result["bedrooms"] = int(token.replace("BR", ""))
                except ValueError:
                    pass
            elif "SQM" in token:
                try:
                    result["floor_area"] = float(token.replace("SQM", ""))
                except ValueError:
                    pass
            elif token.lower() in [k.lower() for k in
                                    list(CITY_ALIASES.keys())]:
                result["city"] = CITY_ALIASES.get(token.lower(), token.title())
            else:
                result["neighbourhood"] = token.title()
        return result

    # SEARCH / property type commands
    # Format: HOUSE 3BR NAIROBI or SEARCH APARTMENT LAGOS 2BR
    result = {"command": "SEARCH", "property_type": None,
              "city": None, "bedrooms": None, "max_price": None}

    if command in TYPE_ALIASES:
        result["property_type"] = TYPE_ALIASES[command.lower()]
    elif command == "SEARCH" and len(tokens) > 1:
        ptype = tokens[1].lower()
        if ptype in TYPE_ALIASES:
            result["property_type"] = TYPE_ALIASES[ptype]
            tokens = [tokens[0]] + tokens[2:]

    for token in tokens[1:]:
        token_lower = token.lower()
        if token_lower in CITY_ALIASES:
            result["city"] = CITY_ALIASES[token_lower]
        elif "BR" in token.upper():
            try:
                result["bedrooms"] = int(token.upper().replace("BR", ""))
            except ValueError:
                pass
        elif token.isdigit():
            result["max_price"] = float(token)

    return result


def format_help_sms() -> str:
    return (
        "AfriProp Commands:\n"
        "SEARCH 2BR NAIROBI\n"
        "HOUSE 3BR LAGOS\n"
        "VALE 2BR WESTLANDS 80SQM\n"
        "LIST - submit property\n"
        "RENT - check payments\n"
        "HELP - this menu"
    )
