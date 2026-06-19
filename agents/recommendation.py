from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data.destinations import normalize_destination
from utils.display import format_hotels_for_display, format_itinerary_for_display
from utils.structured_output import invoke_trip_recommendations
from utils.state_helpers import ensure_trip_defaults

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")


def recommendation_agent(state):
    state = ensure_trip_defaults(state)
    destination = normalize_destination(state["destination"])
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    itinerary = format_itinerary_for_display(state["itinerary"])
    hotel_info = format_hotels_for_display(state["hotels"])
    budget = state.get("budget_breakdown", {})
    preferences = state.get("preferences", {})
    places_data = state.get("places", {})

    prompt = f"""
    You are a personal travel advisor for {destination}, India.

    Travelers: {travelers}
    Rooms required: {rooms_required}
    Preferences: {preferences}
    Budget context (remaining after stay): {budget}

    Itinerary:
    {itinerary}

    Selected stay:
    {hotel_info}

    Available places reference (inspiration only — do NOT list all places):
    {places_data}

    Create personalized TOP EXPERIENCES for THIS specific trip.
    Return exactly 4 ranked top_experiences answering: "What should THESE travelers prioritize?"

    Each experience must include:
    - title (specific place or activity name)
    - reason (why it fits this itinerary and group)
    - estimated_spend (integer INR for the group, not a string)
    - preference_match (how it aligns with traveler preferences)

    travelers must be integer {travelers}.
    Do NOT repeat a full restaurant/attraction directory.
    """

    recommendations = invoke_trip_recommendations(
        llm, prompt, destination, travelers
    )
    recommendations["rooms_required"] = rooms_required

    state["recommendations"] = recommendations
    state["destination"] = destination

    return state
