from data.destinations import normalize_destination
from models.schemas import PlaceItem, PlaceRecommendations
from tools.places_client import get_places
from utils.state_helpers import ensure_trip_defaults


def places_agent(state):
    state = ensure_trip_defaults(state)
    destination = normalize_destination(state["destination"])
    raw_places = get_places(destination)

    places = PlaceRecommendations(
        destination=destination,
        restaurants=[
            PlaceItem(
                name=item["name"],
                description=item["description"],
                category="restaurant",
            )
            for item in raw_places["restaurants"]
        ],
        attractions=[
            PlaceItem(
                name=item["name"],
                description=item["description"],
                category="attraction",
            )
            for item in raw_places["attractions"]
        ],
        hidden_gems=[
            PlaceItem(
                name=item["name"],
                description=item["description"],
                category="hidden_gem",
            )
            for item in raw_places["hidden_gems"]
        ],
        summary=f"Discover restaurants, attractions, and hidden gems in {destination}.",
    )

    state["places"] = places.model_dump()
    state["destination"] = destination

    return state
