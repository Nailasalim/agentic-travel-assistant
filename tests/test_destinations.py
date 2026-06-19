"""Quick tests for destination-aware MCP servers."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from data.destinations import get_hotels_for_destination, normalize_destination
from tools.hotel_client import get_hotels
from tools.places_client import get_places


def test_normalize_destination():
    assert normalize_destination("goa") == "Goa"
    assert normalize_destination("JAIPUR") == "Jaipur"


def test_hotels_vary_by_destination():
    goa = get_hotels_for_destination("Goa")
    jaipur = get_hotels_for_destination("Jaipur")
    assert goa[0]["name"] != jaipur[0]["name"]


def test_mcp_hotel_search():
    hotels = get_hotels("Munnar")
    assert len(hotels) >= 1
    assert hotels[0]["destination"] == "Munnar"


def test_mcp_places_search():
    places = get_places("Ooty")
    assert len(places["restaurants"]) >= 1
    assert len(places["attractions"]) >= 1
    assert len(places["hidden_gems"]) >= 1


if __name__ == "__main__":
    test_normalize_destination()
    test_hotels_vary_by_destination()
    test_mcp_hotel_search()
    test_mcp_places_search()
    print("All destination/MCP tests passed.")
