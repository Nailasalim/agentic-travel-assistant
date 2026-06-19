"""Verify budget consistency with hotel selection."""

from agents.budget import budget_agent
from services.trip_update import apply_stay_selection
from utils.stay import compute_stay_total, select_stay_option


def test_budget_uses_actual_hotel_cost():
    state = {
        "destination": "Varkala",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
        "hotels": {
            "selected_hotel": "Cliff View Resort",
            "selected_hotel_total_cost": 12800,
            "recommendations": [
                {
                    "name": "Cliff View Resort",
                    "price_per_night": 3200,
                    "total_stay_cost": 12800,
                    "is_recommended": True,
                }
            ],
        },
    }

    result = budget_agent(state)
    breakdown = result["budget_breakdown"]

    assert breakdown["hotel_total"] == 12800
    assert breakdown["remaining_budget"] == 30000 - 12800
    assert breakdown["selected_hotel_name"] == "Cliff View Resort"
    assert breakdown["travelers"] == 2
    assert breakdown["rooms_required"] == 1
    assert breakdown["food"] + breakdown["transport"] + breakdown["activities"] == breakdown["remaining_budget"]


def test_room_based_stay_cost():
    total = compute_stay_total(1800, 1, 4)
    assert total == 7200

    total_two_rooms = compute_stay_total(1800, 2, 4)
    assert total_two_rooms == 14400


def test_stay_switching_updates_budget():
    state = {
        "destination": "Varkala",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
        "preferences": {},
        "places": {},
        "itinerary": {
            "destination": "Varkala",
            "total_days": 4,
            "travelers": 2,
            "summary": "Test",
            "days": [],
        },
        "hotels": {
            "selected_hotel": "Cliff View Resort",
            "selected_hotel_total_cost": 12800,
            "travelers": 2,
            "rooms_needed": 1,
            "recommendations": [
                {
                    "name": "Cliff View Resort",
                    "price_per_night": 3200,
                    "hotel_type": "Beach Resort",
                    "reason": "A",
                    "fits_budget": True,
                    "total_stay_cost": 12800,
                    "is_recommended": True,
                },
                {
                    "name": "Varkala Beach Hostel",
                    "price_per_night": 1800,
                    "hotel_type": "Budget",
                    "reason": "B",
                    "fits_budget": True,
                    "total_stay_cost": 7200,
                    "is_recommended": False,
                },
            ],
        },
        "budget_breakdown": {
            "remaining_budget": 17200,
            "hotel_total": 12800,
        },
        "recommendations": {
            "destination": "Varkala",
            "travelers": 2,
            "rooms_required": 1,
            "summary": "Old",
            "top_experiences": [],
        },
    }

    # Mock recommendation to avoid LLM - patch in test file
    from unittest.mock import patch

    fallback = {
        "destination": "Varkala",
        "travelers": 2,
        "rooms_required": 1,
        "summary": "Updated",
        "top_experiences": [],
    }

    with patch(
        "services.trip_update.recommendation_agent",
        side_effect=lambda s: {**s, "recommendations": fallback},
    ):
        updated = apply_stay_selection(state, "Varkala Beach Hostel")

    assert updated["hotels"]["selected_hotel"] == "Varkala Beach Hostel"
    assert updated["budget_breakdown"]["hotel_total"] == 7200
    assert updated["budget_breakdown"]["remaining_budget"] == 22800


if __name__ == "__main__":
    test_budget_uses_actual_hotel_cost()
    test_room_based_stay_cost()
    test_stay_switching_updates_budget()
    print("All budget tests passed.")
