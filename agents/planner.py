from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data.destinations import get_destination_highlights, normalize_destination
from models.schemas import ItineraryPlan
from utils.state_helpers import ensure_trip_defaults

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")
structured_llm = llm.with_structured_output(ItineraryPlan)


def _format_places_for_planner(places: dict) -> str:
    if not places:
        return "No place data available."

    lines = []
    for label, key in [
        ("Restaurants", "restaurants"),
        ("Attractions", "attractions"),
        ("Hidden gems", "hidden_gems"),
    ]:
        items = places.get(key, [])
        if items:
            lines.append(f"{label}:")
            for item in items:
                lines.append(f"  - {item.get('name')}: {item.get('description')}")
    return "\n".join(lines)


def planner_agent(state):
    state = ensure_trip_defaults(state)
    destination = normalize_destination(state["destination"])
    days = state["days"]
    budget = state["budget"]
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    modification_feedback = state.get("modification_feedback", "")
    highlights = get_destination_highlights(destination)
    places_context = _format_places_for_planner(state.get("places", {}))

    feedback_section = ""
    if modification_feedback:
        feedback_section = f"""
    The user requested changes to the previous itinerary:
    {modification_feedback}

    Revise the itinerary to address this feedback.
    """

    prompt = f"""
    Create a detailed {days}-day travel itinerary for {destination}, India.

    Travelers: {travelers} people
    Rooms required: {rooms_required}
    Total trip budget: INR {budget} for the entire group (NOT per person)
    Per-person budget guide: INR {budget // max(travelers, 1):,}

    Destination highlights: {highlights}

    Use these REAL place names in activities and meals (do not use generic labels):
    {places_context}

    Rules:
    - Name specific restaurants, beaches, temples, and attractions from the list above.
    - Never write generic items like "visit beach", "local restaurant", or "ayurvedic massage".
    - Use exact venue names such as "Dinner at Trattorias Restaurant" or "Visit Papanasam Beach".
    - Scale activity costs for {travelers} travelers where relevant.
    {feedback_section}
    """

    plan: ItineraryPlan = structured_llm.invoke(prompt)
    plan.destination = destination
    plan.total_days = days
    plan.travelers = travelers

    state["itinerary"] = plan.model_dump()
    state["destination"] = destination

    return state
