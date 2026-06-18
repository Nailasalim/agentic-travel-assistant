from typing import TypedDict

class TravelState(TypedDict):
    destination: str
    days: int
    budget: int

    itinerary: str
    hotels: str
    budget_breakdown: dict

    preferences: dict