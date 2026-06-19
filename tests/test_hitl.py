"""
Human-in-the-Loop (HITL) test script for the travel planning graph.

Demonstrates LangGraph interrupt + Command(resume=...) with MemorySaver.
"""
import uuid
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.types import Command

from graph.travel_graph import app


def run_scenario(name, thread_id, initial_input, decisions):
    print(f"\n{'=' * 60}")
    print(f"SCENARIO: {name}")
    print(f"{'=' * 60}")

    config = {"configurable": {"thread_id": thread_id}}

    app.invoke(initial_input, config=config)
    snapshot = app.get_state(config)

    assert snapshot.interrupts, "Expected interrupt after planner + approval"
    payload = snapshot.interrupts[0].value
    print("\n[INTERRUPT] Awaiting human approval")
    print(f"  Destination: {payload['destination']}")
    print(f"  Budget: {payload['budget']}")
    print(f"  Itinerary preview: {payload['itinerary'][:200]}...")

    for step, decision in enumerate(decisions, start=1):
        print(f"\n[RESUME #{step}] action={decision['action']}")

        app.invoke(Command(resume=decision), config=config)
        snapshot = app.get_state(config)

        if snapshot.interrupts:
            payload = snapshot.interrupts[0].value
            print("[INTERRUPT] Awaiting human approval again")
            print(f"  Itinerary preview: {payload['itinerary'][:200]}...")
            continue

        status = snapshot.values.get("approval_status")
        if status == "rejected":
            print("[STOPPED] Trip rejected")
            print(f"  Message: {snapshot.values.get('approval_message')}")
            return snapshot

        if snapshot.values.get("hotels"):
            print("[COMPLETED] Full trip plan generated")
            hotels = snapshot.values["hotels"]
            if isinstance(hotels, dict):
                print(f"  Hotels: {hotels.get('summary', hotels)}")
            else:
                print(f"  Hotels preview: {str(hotels)[:200]}...")
            return snapshot

    raise RuntimeError("Scenario did not reach a terminal state")


if __name__ == "__main__":
    base_input = {
        "destination": "Goa",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
        "preferences": {"hotel_type": "Beach Resort"},
    }

    run_scenario(
        name="Approve flow",
        thread_id=f"hitl_approve_{uuid.uuid4().hex[:8]}",
        initial_input={**base_input, "thread_id": "hitl_approve"},
        decisions=[{"action": "approve", "feedback": ""}],
    )

    run_scenario(
        name="Reject flow",
        thread_id=f"hitl_reject_{uuid.uuid4().hex[:8]}",
        initial_input={**base_input, "thread_id": "hitl_reject"},
        decisions=[{"action": "reject", "feedback": ""}],
    )

    run_scenario(
        name="Modify then approve flow",
        thread_id=f"hitl_modify_{uuid.uuid4().hex[:8]}",
        initial_input={**base_input, "thread_id": "hitl_modify"},
        decisions=[
            {
                "action": "modify",
                "feedback": "Add more beach activities and reduce museum visits.",
            },
            {"action": "approve", "feedback": ""},
        ],
    )

    print("\nAll HITL scenarios completed successfully.")
