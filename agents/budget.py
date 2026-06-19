from data.destinations import normalize_destination
from models.schemas import BudgetBreakdown
from utils.stay import compute_stay_total
from utils.state_helpers import ensure_trip_defaults


def budget_agent(state):
    state = ensure_trip_defaults(state)
    total_budget = state["budget"]
    days = state["days"]
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    destination = normalize_destination(state["destination"])
    hotels = state.get("hotels", {})

    selected_name = hotels.get("selected_hotel", "")
    hotel_total = float(hotels.get("selected_hotel_total_cost", 0))

    if not hotel_total and hotels.get("recommendations"):
        primary = next(
            (h for h in hotels["recommendations"] if h.get("is_recommended")),
            hotels["recommendations"][0],
        )
        hotel_total = float(
            primary.get(
                "total_stay_cost",
                compute_stay_total(
                    primary.get("price_per_night", 0), rooms_required, days
                ),
            )
        )
        selected_name = primary.get("name", selected_name)

    remaining = max(0.0, total_budget - hotel_total)

    food = round(remaining * 0.42, 2)
    transport = round(remaining * 0.28, 2)
    activities = round(remaining - food - transport, 2)

    within_budget = hotel_total <= total_budget
    per_person = total_budget / max(travelers, 1)

    rationale = (
        f"Stay at '{selected_name}' costs ₹{hotel_total:,.0f} "
        f"({rooms_required} room(s) × {days} nights). "
        f"Remaining ₹{remaining:,.0f} is allocated for {travelers} travelers: "
        f"42% food (₹{food:,.0f}), 28% transport (₹{transport:,.0f}), "
        f"30% activities (₹{activities:,.0f})."
    )

    breakdown = BudgetBreakdown(
        travelers=travelers,
        rooms_required=rooms_required,
        days=days,
        total_budget=float(total_budget),
        selected_hotel_name=selected_name,
        hotel_nights=days,
        hotel_total=hotel_total,
        remaining_budget=remaining,
        food=food,
        transport=transport,
        activities=activities,
        total=float(total_budget),
        within_budget=within_budget,
        per_person_estimate=round(per_person, 2),
        notes=(
            f"Budget plan for {travelers} travelers, {rooms_required} room(s), "
            f"{days} days in {destination}. Based on selected stay: {selected_name}."
        ),
        allocation_rationale=rationale,
    )

    state["budget_breakdown"] = breakdown.model_dump()

    return state
