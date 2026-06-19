from typing import Any

from utils.display import (
    format_budget_for_display,
    format_hotels_for_display,
    format_itinerary_for_display,
    format_places_for_display,
    format_recommendations_for_display,
)


def serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    """Return graph state as JSON-serializable structured output."""
    if not state:
        return {}

    return {
        "destination": state.get("destination"),
        "days": state.get("days"),
        "budget": state.get("budget"),
        "travelers": state.get("travelers", 1),
        "rooms_required": state.get("rooms_required", 1),
        "thread_id": state.get("thread_id"),
        "preferences": state.get("preferences", {}),
        "itinerary": state.get("itinerary"),
        "hotels": state.get("hotels"),
        "places": state.get("places"),
        "budget_breakdown": format_budget_for_display(state.get("budget_breakdown", {})),
        "recommendations": state.get("recommendations"),
        "budget_feasible": state.get("budget_feasible"),
        "budget_error": state.get("budget_error"),
        "approval_status": state.get("approval_status"),
        "approval_message": state.get("approval_message"),
        "modification_feedback": state.get("modification_feedback"),
        "display": {
            "itinerary": format_itinerary_for_display(state.get("itinerary")),
            "hotels": format_hotels_for_display(state.get("hotels")),
            "places": format_places_for_display(state.get("places")),
            "recommendations": format_recommendations_for_display(
                state.get("recommendations")
            ),
        },
    }
