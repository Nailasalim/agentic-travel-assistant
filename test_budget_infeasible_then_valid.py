"""Test infeasible budget then valid trip on the same thread."""

import uuid

from fastapi.testclient import TestClient

from api.main import app as fastapi_app
from graph.travel_graph import app as travel_app


def test_budget_infeasible_then_valid_trip_graph():
    thread_id = f"feasibility_{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    travel_app.invoke(
        {
            "thread_id": thread_id,
            "destination": "Varkala",
            "days": 4,
            "budget": 5000,
            "travelers": 2,
            "rooms_required": 1,
            "preferences": {},
            "budget_feasible": True,
            "budget_error": {},
        },
        config=config,
    )

    snap_infeasible = travel_app.get_state(config)
    assert snap_infeasible.values.get("budget_feasible") is False
    assert not snap_infeasible.interrupts
    assert not snap_infeasible.values.get("itinerary")

    travel_app.invoke(
        {
            "thread_id": thread_id,
            "destination": "Varkala",
            "days": 4,
            "budget": 50000,
            "travelers": 2,
            "rooms_required": 1,
            "preferences": {},
            "budget_feasible": True,
            "budget_error": {},
            "modification_feedback": "",
        },
        config=config,
    )

    snap_valid = travel_app.get_state(config)
    assert snap_valid.values.get("budget_feasible") is True
    assert snap_valid.values.get("itinerary")
    assert len(snap_valid.interrupts) == 1
    assert snap_valid.interrupts[0].value.get("action_required") == "itinerary_approval"


def test_budget_infeasible_then_valid_trip_api():
    client = TestClient(fastapi_app)
    thread_id = f"api_feasibility_{uuid.uuid4().hex[:8]}"

    infeasible = client.post(
        "/plan-trip",
        json={
            "destination": "Varkala",
            "days": 4,
            "budget": 5000,
            "travelers": 2,
            "rooms_required": 1,
            "thread_id": thread_id,
            "preferences": {},
        },
    )
    assert infeasible.status_code == 200
    body = infeasible.json()
    assert body["status"] == "budget_infeasible"
    assert body.get("budget_error")
    assert "state" not in body

    feasible = client.post(
        "/plan-trip",
        json={
            "destination": "Varkala",
            "days": 4,
            "budget": 50000,
            "travelers": 2,
            "rooms_required": 1,
            "thread_id": thread_id,
            "preferences": {},
        },
    )
    assert feasible.status_code == 200
    result = feasible.json()
    assert result["status"] == "awaiting_approval"
    assert result.get("approval_payload")
    assert result["status"] != "error"


if __name__ == "__main__":
    test_budget_infeasible_then_valid_trip_graph()
    test_budget_infeasible_then_valid_trip_api()
    print("test_budget_infeasible_then_valid_trip passed.")
