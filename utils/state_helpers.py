"""Normalize trip input fields before agents run."""


def ensure_trip_defaults(state: dict) -> dict:
    """Apply defensive defaults so every node receives a consistent TravelState."""
    state["travelers"] = int(state.get("travelers") or 1)
    state["rooms_required"] = int(state.get("rooms_required") or 1)
    state["preferences"] = state.get("preferences") or {}
    state["destination"] = state.get("destination", "")
    state["days"] = int(state.get("days") or 1)
    state["budget"] = int(state.get("budget") or 0)
    state["thread_id"] = state.get("thread_id", "default_user")
    return state


def reset_stale_trip_fields(state: dict) -> dict:
    """Clear stale fields when starting a new planning attempt on a thread."""
    state["budget_feasible"] = True
    state["budget_error"] = {}
    state["modification_feedback"] = ""
    state.pop("approval_status", None)
    if state.get("approval_message") == "Your budget is too low for this trip configuration.":
        state.pop("approval_message", None)
    return state
