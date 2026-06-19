from langgraph.types import interrupt

from data.destinations import estimate_hotel_cost, normalize_destination
from utils.display import format_itinerary_for_display


def approval_agent(state):
    """
    Pause workflow after itinerary generation and wait for human decision.

    Uses LangGraph interrupt() so execution can resume via Command(resume=...)
    with the same thread_id and checkpointer.
    """
    destination = normalize_destination(state["destination"])
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    days = state["days"]
    budget = state["budget"]
    preferences = state.get("preferences", {})
    hotel_preference = preferences.get("hotel_type", "Any")
    hotel_estimate = estimate_hotel_cost(
        destination, days, travelers, hotel_preference, rooms_required
    )
    itinerary_display = format_itinerary_for_display(state.get("itinerary"))

    human_decision = interrupt(
        {
            "action_required": "itinerary_approval",
            "trip_summary": {
                "destination": destination,
                "travelers": travelers,
                "rooms_required": rooms_required,
                "days": days,
                "budget": budget,
                "stay_preference": hotel_preference,
                "estimated_stay_cost": hotel_estimate["estimated_hotel_total"],
                "estimated_nightly_rate": hotel_estimate["estimated_nightly_rate"],
            },
            "destination": destination,
            "travelers": travelers,
            "rooms_required": rooms_required,
            "days": days,
            "budget": budget,
            "stay_preference": hotel_preference,
            "estimated_stay_cost": hotel_estimate["estimated_hotel_total"],
            "itinerary": itinerary_display,
            "itinerary_plan": state.get("itinerary"),
            "message": "Review your trip summary and itinerary, then approve or request changes.",
        }
    )

    action, feedback = _parse_decision(human_decision)

    status_map = {
        "approve": "approved",
        "reject": "rejected",
        "modify": "modification_requested",
    }
    state["approval_status"] = status_map[action]

    if action == "modify":
        state["modification_feedback"] = feedback
    else:
        state["modification_feedback"] = ""

    if action == "reject":
        state["approval_message"] = (
            "Trip planning stopped. The itinerary was rejected by the user."
        )
    elif action == "approve":
        state["approval_message"] = "Itinerary approved. Finding stays and finalizing your plan."
    else:
        state["approval_message"] = (
            "Modification requested. Regenerating itinerary with your feedback."
        )

    return state


def _parse_decision(human_decision):
    if isinstance(human_decision, dict):
        action = str(human_decision.get("action", "reject")).lower()
        feedback = str(human_decision.get("feedback", ""))
    elif isinstance(human_decision, str):
        action = human_decision.lower()
        feedback = ""
    else:
        action = "reject"
        feedback = ""

    if action not in {"approve", "reject", "modify"}:
        action = "reject"

    return action, feedback
