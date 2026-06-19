"""Update completed trip state after stay selection without restarting workflow."""

from agents.budget import budget_agent
from agents.planner import planner_agent
from agents.recommendation import recommendation_agent
from utils.stay import select_stay_option


def apply_stay_selection(state: dict, hotel_name: str) -> dict:
    """
    Select a stay, recalculate budget and recommendations.
    Regenerates itinerary if remaining budget changes by more than 15%.
    """
    days = state["days"]
    rooms_required = state.get("rooms_required", state.get("rooms_needed", 1))

    old_breakdown = state.get("budget_breakdown", {})
    old_remaining = float(old_breakdown.get("remaining_budget", state["budget"]))

    state["hotels"] = select_stay_option(
        state["hotels"], hotel_name, days, rooms_required
    )

    state = budget_agent(state)
    new_remaining = float(state["budget_breakdown"].get("remaining_budget", 0))

    if old_remaining > 0:
        change_ratio = abs(new_remaining - old_remaining) / old_remaining
    else:
        change_ratio = 1.0 if new_remaining != old_remaining else 0.0

    if change_ratio > 0.15:
        state["modification_feedback"] = (
            f"Stay changed to {hotel_name}. "
            f"Remaining activity budget is now ₹{new_remaining:,.0f}. "
            "Adjust activities and dining to fit the updated budget."
        )
        state = planner_agent(state)
        state["modification_feedback"] = ""

    state = recommendation_agent(state)
    return state
