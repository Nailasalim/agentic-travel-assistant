from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data.destinations import normalize_destination
from models.schemas import HotelRecommendation
from tools.hotel_client import get_hotels
from utils.stay import normalize_hotel_recommendations
from utils.state_helpers import ensure_trip_defaults

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")
structured_llm = llm.with_structured_output(HotelRecommendation)


def hotel_agent(state):
    state = ensure_trip_defaults(state)
    budget = state["budget"]
    days = state["days"]
    travelers = state.get("travelers", 1)
    rooms_required = state.get("rooms_required", 1)
    destination = normalize_destination(state["destination"])

    hotels = get_hotels(destination)
    preferences = state.get("preferences", {})
    hotel_preference = preferences.get("hotel_type", "Any")

    max_stay_budget = budget * 0.5
    nightly_cap = max_stay_budget / max(days * rooms_required, 1)

    prompt = f"""
    You are a stay recommendation expert for {destination}, India.

    Travelers: {travelers}
    Rooms required: {rooms_required} (user-specified)
    Total trip budget (entire group): INR {budget}
    Maximum recommended stay spend: INR {max_stay_budget:.0f}
    Nightly rate cap per room: INR {nightly_cap:.0f}
    Trip length: {days} nights

    User stay preference: {hotel_preference}

    Available stays:
    {hotels}

    Return exactly 3 options from the list above:
    1. Recommended stay (is_recommended=true) — best match for preference and budget
    2. Alternative stay 1 (is_recommended=false)
    3. Alternative stay 2 (is_recommended=false)

    For each option set total_stay_cost = price_per_night * {days} * {rooms_required}.
    Set fits_budget true when total_stay_cost <= {max_stay_budget:.0f}.
    Explain suitability for {travelers} travelers and {rooms_required} room(s).
    """

    recommendation: HotelRecommendation = structured_llm.invoke(prompt)
    recommendation.destination = destination
    recommendation.travelers = travelers
    recommendation.rooms_needed = rooms_required
    recommendation.preference_used = hotel_preference

    hotels_dict = recommendation.model_dump()
    hotels_dict = normalize_hotel_recommendations(
        hotels_dict, days, rooms_required, max_stay_budget
    )

    state["hotels"] = hotels_dict
    state["destination"] = destination

    return state
