from mcp.server.fastmcp import FastMCP

from data.destinations import get_hotels_for_destination, normalize_destination

mcp = FastMCP("hotel-search-server")


@mcp.tool()
def search_hotels(location: str) -> list:
    """Search for hotels in a given location in India."""
    destination = normalize_destination(location)
    hotels = get_hotels_for_destination(destination)
    return [{**hotel, "destination": destination} for hotel in hotels]


if __name__ == "__main__":
    mcp.run()
