"""Destination registry and per-city hotel datasets for India."""

SUPPORTED_DESTINATIONS = [
    "Goa",
    "Jaipur",
    "Munnar",
    "Varkala",
    "Coorg",
    "Shillong",
    "Ooty",
    "Manali",
]

_ALIASES = {
    "goa": "Goa",
    "jaipur": "Jaipur",
    "pink city": "Jaipur",
    "munnar": "Munnar",
    "varkala": "Varkala",
    "coorg": "Coorg",
    "kodagu": "Coorg",
    "shillong": "Shillong",
    "ooty": "Ooty",
    "udagamandalam": "Ooty",
    "manali": "Manali",
}

DESTINATION_HIGHLIGHTS = {
    "Goa": "Beaches, Portuguese heritage, seafood, nightlife, and water sports.",
    "Jaipur": "Rajasthani forts, palaces, bazaars, heritage hotels, and desert cuisine.",
    "Munnar": "Tea plantations, misty hills, wildlife, and Kerala homestays.",
    "Varkala": "Cliff beaches, Ayurveda, relaxed coastal vibes, and yoga retreats.",
    "Coorg": "Coffee estates, waterfalls, trekking, and Kodava culture.",
    "Shillong": "Living root bridges nearby, lakes, music culture, and Northeast cuisine.",
    "Ooty": "Nilgiri toy train, botanical gardens, hill-station weather, and tea gardens.",
    "Manali": "Himalayan views, adventure sports, Old Manali cafes, and snow activities.",
}

HOTELS_BY_DESTINATION = {
    "Goa": [
        {"name": "Holiday Inn Goa", "price": 3500, "type": "Beach Resort"},
        {"name": "Goa Paradise", "price": 2500, "type": "Budget"},
        {"name": "Luxury Sands", "price": 6000, "type": "Luxury"},
    ],
    "Jaipur": [
        {"name": "Heritage Haveli Jaipur", "price": 4200, "type": "Heritage"},
        {"name": "Pink City Inn", "price": 2800, "type": "Budget"},
        {"name": "Rambagh Palace Suite", "price": 8500, "type": "Luxury"},
    ],
    "Munnar": [
        {"name": "Tea Valley Resort", "price": 3800, "type": "Boutique"},
        {"name": "Munnar Green Stay", "price": 2200, "type": "Budget"},
        {"name": "Spice Garden Luxury", "price": 5500, "type": "Luxury"},
    ],
    "Varkala": [
        {"name": "Cliff View Resort", "price": 3200, "type": "Beach Resort"},
        {"name": "Varkala Beach Hostel", "price": 1800, "type": "Budget"},
        {"name": "Ayur Cliff Retreat", "price": 4800, "type": "Boutique"},
    ],
    "Coorg": [
        {"name": "Coffee Estate Homestay", "price": 3000, "type": "Boutique"},
        {"name": "Coorg Valley Lodge", "price": 2400, "type": "Budget"},
        {"name": "Madikeri Heritage Resort", "price": 5200, "type": "Heritage"},
    ],
    "Shillong": [
        {"name": "Shillong Peak View Hotel", "price": 3400, "type": "Boutique"},
        {"name": "Police Bazaar Inn", "price": 2100, "type": "Budget"},
        {"name": "Ri Kynjai Resort", "price": 5800, "type": "Luxury"},
    ],
    "Ooty": [
        {"name": "Nilgiri Hill Resort", "price": 3600, "type": "Boutique"},
        {"name": "Ooty Lake Lodge", "price": 2300, "type": "Budget"},
        {"name": "Savoy Ooty Heritage", "price": 6200, "type": "Heritage"},
    ],
    "Manali": [
        {"name": "Himalayan View Resort", "price": 4000, "type": "Boutique"},
        {"name": "Old Manali Backpackers", "price": 2000, "type": "Budget"},
        {"name": "Snow Peak Luxury", "price": 7000, "type": "Luxury"},
    ],
}


def normalize_destination(location: str) -> str:
    key = location.strip().lower()
    return _ALIASES.get(key, location.strip().title())


def get_hotels_for_destination(location: str) -> list[dict]:
    destination = normalize_destination(location)
    if destination in HOTELS_BY_DESTINATION:
        return HOTELS_BY_DESTINATION[destination]

    return [
        {
            "name": f"{destination} Comfort Inn",
            "price": 3000,
            "type": "Budget",
        },
        {
            "name": f"{destination} Grand Stay",
            "price": 4500,
            "type": "Boutique",
        },
        {
            "name": f"{destination} Premium Resort",
            "price": 6000,
            "type": "Luxury",
        },
    ]


def get_destination_highlights(location: str) -> str:
    destination = normalize_destination(location)
    return DESTINATION_HIGHLIGHTS.get(
        destination,
        f"Explore local culture, cuisine, and landmarks in {destination}, India.",
    )


def rooms_for_travelers(travelers: int) -> int:
    """Estimate rooms needed (2 guests per room, minimum 1)."""
    return max(1, (travelers + 1) // 2)


def estimate_hotel_cost(
    location: str,
    days: int,
    travelers: int,
    hotel_preference: str = "Any",
    rooms_required: int | None = None,
) -> dict:
    """Estimate hotel spend before the hotel agent runs (for HITL preview)."""
    destination = normalize_destination(location)
    hotels = get_hotels_for_destination(destination)

    if hotel_preference and hotel_preference != "Any":
        preferred = [h for h in hotels if h["type"].lower() == hotel_preference.lower()]
        if preferred:
            hotels = preferred

    rooms = rooms_required if rooms_required is not None else rooms_for_travelers(travelers)
    min_price = min(h["price"] for h in hotels)
    avg_nightly = sum(h["price"] for h in hotels) / len(hotels)
    nightly = int(round(avg_nightly))
    total = nightly * days * rooms

    return {
        "estimated_nightly_rate": nightly,
        "minimum_nightly_rate": min_price,
        "rooms_needed": rooms,
        "rooms_required": rooms,
        "estimated_hotel_total": total,
        "nights": days,
    }


def calculate_minimum_feasible_budget(
    location: str,
    days: int,
    travelers: int,
    rooms_required: int,
    hotel_preference: str = "Any",
) -> dict:
    """
    Minimum budget required for a feasible trip.
    minimum = min_stay + min_food + min_transport
    """
    destination = normalize_destination(location)
    hotels = get_hotels_for_destination(destination)

    if hotel_preference and hotel_preference != "Any":
        preferred = [h for h in hotels if h["type"].lower() == hotel_preference.lower()]
        pool = preferred if preferred else hotels
    else:
        pool = hotels

    min_nightly = min(h["price"] for h in pool)
    minimum_stay_cost = min_nightly * days * rooms_required
    minimum_food_cost = travelers * days * 400
    minimum_transport_cost = travelers * days * 250 + days * 150

    minimum_feasible = minimum_stay_cost + minimum_food_cost + minimum_transport_cost

    return {
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "rooms_required": rooms_required,
        "minimum_stay_cost": minimum_stay_cost,
        "minimum_food_cost": minimum_food_cost,
        "minimum_transport_cost": minimum_transport_cost,
        "minimum_feasible_budget": minimum_feasible,
        "cheapest_nightly_rate": min_nightly,
    }


def validate_trip_budget(
    budget: int,
    location: str,
    days: int,
    travelers: int,
    rooms_required: int,
    hotel_preference: str = "Any",
) -> dict:
    """Return feasibility assessment and suggestions if budget is too low."""
    feasibility = calculate_minimum_feasible_budget(
        location, days, travelers, rooms_required, hotel_preference
    )
    minimum = feasibility["minimum_feasible_budget"]
    is_feasible = budget >= minimum
    shortfall = max(0, minimum - budget)

    suggestions = []
    if not is_feasible:
        suggestions = [
            f"Increase budget by at least ₹{shortfall:,}",
            "Reduce number of days",
            "Reduce rooms required",
            "Choose a cheaper stay preference (e.g. Budget)",
        ]

    return {
        **feasibility,
        "user_budget": budget,
        "is_feasible": is_feasible,
        "budget_shortfall": shortfall,
        "suggestions": suggestions,
    }
