"""Tests for schema coercion and budget feasibility validation."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from data.destinations import validate_trip_budget
from utils.coercion import coerce_int
from utils.structured_output import normalize_trip_recommendations


def test_coerce_int_from_string():
    assert coerce_int("2") == 2
    assert coerce_int("800") == 800
    assert coerce_int("₹1,200") == 1200


def test_normalize_trip_recommendations_coerces_strings():
    raw = {
        "destination": "Varkala",
        "travelers": "2",
        "summary": "Test",
        "top_experiences": [
            {
                "title": "Sunset at Varkala Cliff",
                "reason": "Relaxing",
                "estimated_spend": "800",
                "preference_match": "Coastal",
            }
        ],
    }
    result = normalize_trip_recommendations(raw, "Varkala", 2)
    assert result["travelers"] == 2
    assert isinstance(result["travelers"], int)
    assert result["top_experiences"][0]["estimated_spend"] == 800
    assert isinstance(result["top_experiences"][0]["estimated_spend"], int)


def test_low_budget_validation_varkala():
    result = validate_trip_budget(
        budget=5000,
        location="Varkala",
        days=4,
        travelers=2,
        rooms_required=1,
        hotel_preference="Any",
    )
    assert result["is_feasible"] is False
    assert result["budget_shortfall"] > 0
    assert result["minimum_stay_cost"] == 1800 * 4 * 1
    assert len(result["suggestions"]) >= 1


def test_feasible_budget_passes():
    result = validate_trip_budget(
        budget=50000,
        location="Varkala",
        days=4,
        travelers=2,
        rooms_required=1,
    )
    assert result["is_feasible"] is True
    assert result["budget_shortfall"] == 0


if __name__ == "__main__":
    test_coerce_int_from_string()
    test_normalize_trip_recommendations_coerces_strings()
    test_low_budget_validation_varkala()
    test_feasible_budget_passes()
    print("All schema and feasibility tests passed.")
