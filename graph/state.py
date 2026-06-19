from typing import TypedDict, NotRequired


class TravelState(TypedDict):
    destination: str
    days: int
    budget: int
    travelers: int
    rooms_required: int

    itinerary: NotRequired[dict]
    hotels: NotRequired[dict]
    places: NotRequired[dict]
    budget_breakdown: NotRequired[dict]
    thread_id: str
    preferences: dict
    recommendations: NotRequired[dict]

    budget_feasible: NotRequired[bool]
    budget_error: NotRequired[dict]

    approval_status: NotRequired[str]
    modification_feedback: NotRequired[str]
    approval_message: NotRequired[str]
