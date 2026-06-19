from typing import Any, Literal
import traceback

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langgraph.types import Command

from graph.travel_graph import app as travel_app
from api.serializers import serialize_state
from services.trip_update import apply_stay_selection
from data.destinations import normalize_destination, validate_trip_budget

app = FastAPI()


class TripRequest(BaseModel):
    destination: str
    days: int
    budget: int
    travelers: int = Field(default=2, ge=1, le=20)
    rooms_required: int = Field(default=1, ge=1, le=10)
    thread_id: str = "user_1"
    preferences: dict = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    thread_id: str
    action: Literal["approve", "reject", "modify"]
    feedback: str = ""


class SelectStayRequest(BaseModel):
    thread_id: str
    hotel_name: str


def _graph_config(thread_id: str):
    return {"configurable": {"thread_id": thread_id}}


def _trip_input(request: TripRequest) -> dict:
    return {
        "thread_id": request.thread_id,
        "destination": request.destination,
        "days": request.days,
        "budget": request.budget,
        "travelers": request.travelers,
        "rooms_required": request.rooms_required,
        "preferences": request.preferences,
        "budget_feasible": True,
        "budget_error": {},
        "modification_feedback": "",
    }


def _check_budget_feasibility(request: TripRequest) -> dict:
    hotel_preference = request.preferences.get("hotel_type", "Any")
    return validate_trip_budget(
        budget=request.budget,
        location=normalize_destination(request.destination),
        days=request.days,
        travelers=request.travelers,
        rooms_required=request.rooms_required,
        hotel_preference=hotel_preference,
    )


def _format_interrupt_response(thread_id: str, snapshot):
    interrupt_payload = None
    if snapshot.interrupts:
        interrupt_payload = snapshot.interrupts[0].value

    return {
        "status": "awaiting_approval",
        "thread_id": thread_id,
        "approval_payload": interrupt_payload,
        "state": serialize_state(snapshot.values),
    }


def _format_budget_infeasible(thread_id: str, budget_error: dict):
    """Return infeasible response without graph checkpoint data."""
    return {
        "status": "budget_infeasible",
        "thread_id": thread_id,
        "message": "Your budget is too low for this trip configuration.",
        "budget_error": budget_error,
    }


def _format_error(thread_id: str, exc: Exception) -> dict[str, Any]:
    return {
        "status": "error",
        "thread_id": thread_id,
        "message": str(exc),
    }


@app.post("/plan-trip")
def plan_trip(request: TripRequest):
    validation = _check_budget_feasibility(request)
    if not validation["is_feasible"]:
        return _format_budget_infeasible(request.thread_id, validation)

    config = _graph_config(request.thread_id)

    try:
        travel_app.invoke(_trip_input(request), config=config)
    except Exception as exc:
        traceback.print_exc()
        return _format_error(request.thread_id, exc)

    snapshot = travel_app.get_state(config)

    if snapshot.values.get("budget_feasible") is False:
        budget_error = snapshot.values.get("budget_error") or validation
        return _format_budget_infeasible(request.thread_id, budget_error)

    if snapshot.interrupts:
        return _format_interrupt_response(request.thread_id, snapshot)

    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "result": serialize_state(snapshot.values),
    }


@app.get("/plan-trip/status/{thread_id}")
def plan_trip_status(thread_id: str):
    config = _graph_config(thread_id)
    snapshot = travel_app.get_state(config)

    if not snapshot.values:
        raise HTTPException(status_code=404, detail="No trip found for this thread_id")

    if snapshot.values.get("budget_feasible") is False:
        budget_error = snapshot.values.get("budget_error", {})
        return _format_budget_infeasible(thread_id, budget_error)

    if snapshot.interrupts:
        return _format_interrupt_response(thread_id, snapshot)

    approval_status = snapshot.values.get("approval_status")
    if approval_status == "rejected":
        return {
            "status": "rejected",
            "thread_id": thread_id,
            "message": snapshot.values.get("approval_message"),
            "state": serialize_state(snapshot.values),
        }

    return {
        "status": "completed",
        "thread_id": thread_id,
        "result": serialize_state(snapshot.values),
    }


@app.post("/plan-trip/resume")
def resume_trip(request: ApprovalRequest):
    if request.action == "modify" and not request.feedback.strip():
        raise HTTPException(
            status_code=400,
            detail="feedback is required when action is modify",
        )

    config = _graph_config(request.thread_id)
    snapshot = travel_app.get_state(config)

    if not snapshot.interrupts:
        raise HTTPException(
            status_code=400,
            detail="No pending approval interrupt for this thread_id",
        )

    resume_value = {"action": request.action, "feedback": request.feedback}

    try:
        travel_app.invoke(Command(resume=resume_value), config=config)
    except Exception as exc:
        traceback.print_exc()
        return _format_error(request.thread_id, exc)

    snapshot = travel_app.get_state(config)

    if snapshot.interrupts:
        return _format_interrupt_response(request.thread_id, snapshot)

    approval_status = snapshot.values.get("approval_status")
    if approval_status == "rejected":
        return {
            "status": "rejected",
            "thread_id": request.thread_id,
            "message": snapshot.values.get("approval_message"),
            "state": serialize_state(snapshot.values),
        }

    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "result": serialize_state(snapshot.values),
    }


@app.post("/plan-trip/select-stay")
def select_stay(request: SelectStayRequest):
    config = _graph_config(request.thread_id)
    snapshot = travel_app.get_state(config)

    if not snapshot.values:
        raise HTTPException(status_code=404, detail="No trip found for this thread_id")

    if not snapshot.values.get("hotels"):
        raise HTTPException(
            status_code=400,
            detail="Stay can only be selected after trip planning is complete",
        )

    try:
        updated = apply_stay_selection(dict(snapshot.values), request.hotel_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        traceback.print_exc()
        return _format_error(request.thread_id, exc)

    travel_app.update_state(
        config,
        {
            "hotels": updated.get("hotels"),
            "budget_breakdown": updated.get("budget_breakdown"),
            "recommendations": updated.get("recommendations"),
            "itinerary": updated.get("itinerary"),
        },
    )

    snapshot = travel_app.get_state(config)

    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "result": serialize_state(snapshot.values),
    }
