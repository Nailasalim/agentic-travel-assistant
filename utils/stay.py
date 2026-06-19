"""Stay selection and cost calculation helpers."""

from copy import deepcopy

from utils.coercion import coerce_int


def compute_stay_total(price_per_night: int, rooms_required: int, nights: int) -> int:
    return coerce_int(price_per_night) * coerce_int(rooms_required) * coerce_int(nights)


def normalize_hotel_recommendations(
    hotels: dict, days: int, rooms_required: int, max_stay_budget: float | None = None
) -> dict:
    """Recalculate total_stay_cost and selected stay for all options."""
    updated = deepcopy(hotels)
    rooms = coerce_int(rooms_required, 1)
    nights = coerce_int(days, 1)

    for option in updated.get("recommendations", []):
        option["total_stay_cost"] = compute_stay_total(
            option.get("price_per_night", 0), rooms, nights
        )
        if max_stay_budget is not None:
            option["fits_budget"] = option["total_stay_cost"] <= max_stay_budget

    selected_name = updated.get("selected_hotel", "")
    selected = next(
        (h for h in updated.get("recommendations", []) if h.get("name") == selected_name),
        None,
    )
    if not selected and updated.get("recommendations"):
        selected = updated["recommendations"][0]

    if selected:
        for option in updated["recommendations"]:
            option["is_recommended"] = option.get("name") == selected.get("name")
        updated["selected_hotel"] = selected["name"]
        updated["selected_hotel_total_cost"] = selected["total_stay_cost"]

    updated["rooms_needed"] = rooms
    return updated


def select_stay_option(hotels: dict, hotel_name: str, days: int, rooms_required: int) -> dict:
    updated = deepcopy(hotels)
    match = next(
        (h for h in updated.get("recommendations", []) if h.get("name") == hotel_name),
        None,
    )
    if not match:
        raise ValueError(f"Stay option not found: {hotel_name}")

    updated["selected_hotel"] = hotel_name
    for option in updated.get("recommendations", []):
        option["is_recommended"] = option.get("name") == hotel_name
        option["total_stay_cost"] = compute_stay_total(
            option.get("price_per_night", 0), rooms_required, days
        )

    updated["selected_hotel_total_cost"] = compute_stay_total(
        match.get("price_per_night", 0), rooms_required, days
    )
    updated["rooms_needed"] = rooms_required
    return updated
