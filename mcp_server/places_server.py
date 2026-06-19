from mcp.server.fastmcp import FastMCP

from data.places import get_attractions, get_hidden_gems, get_restaurants
from data.destinations import normalize_destination

mcp = FastMCP("places-search-server")


@mcp.tool()
def search_restaurants(destination: str) -> list:
    """Search for restaurants in a given destination in India."""
    city = normalize_destination(destination)
    return [{**item, "destination": city, "category": "restaurant"} for item in get_restaurants(city)]


@mcp.tool()
def search_attractions(destination: str) -> list:
    """Search for attractions in a given destination in India."""
    city = normalize_destination(destination)
    return [{**item, "destination": city, "category": "attraction"} for item in get_attractions(city)]


@mcp.tool()
def search_hidden_gems(destination: str) -> list:
    """Search for hidden gems in a given destination in India."""
    city = normalize_destination(destination)
    return [{**item, "destination": city, "category": "hidden_gem"} for item in get_hidden_gems(city)]


if __name__ == "__main__":
    mcp.run()
