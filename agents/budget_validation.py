from data.destinations import normalize_destination, validate_trip_budget
from utils.state_helpers import ensure_trip_defaults


def budget_validation_agent(state):
    state = ensure_trip_defaults(state)

    destination = normalize_destination(state["destination"])
    days = state["days"]
    budget = state["budget"]
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    preferences = state.get("preferences", {})
    hotel_preference = preferences.get("hotel_type", "Any")

    result = validate_trip_budget(
        budget=budget,
        location=destination,
        days=days,
        travelers=travelers,
        rooms_required=rooms_required,
        hotel_preference=hotel_preference,
    )

    state["destination"] = destination
    state["budget_feasible"] = result["is_feasible"]

    if result["is_feasible"]:
        state["budget_error"] = {}
        if state.get("approval_message") == "Your budget is too low for this trip configuration.":
            state.pop("approval_message", None)
    else:
        state["budget_error"] = result
        state["approval_message"] = "Your budget is too low for this trip configuration."

    return state
