import asyncio

from tools.mcp_client import call_mcp_tool


async def search_places_via_mcp(destination: str):
    restaurants, attractions, hidden_gems = await asyncio.gather(
        call_mcp_tool(
            "mcp_server/places_server.py",
            "search_restaurants",
            {"destination": destination},
        ),
        call_mcp_tool(
            "mcp_server/places_server.py",
            "search_attractions",
            {"destination": destination},
        ),
        call_mcp_tool(
            "mcp_server/places_server.py",
            "search_hidden_gems",
            {"destination": destination},
        ),
    )

    return {
        "restaurants": restaurants,
        "attractions": attractions,
        "hidden_gems": hidden_gems,
    }


def get_places(destination: str):
    return asyncio.run(search_places_via_mcp(destination))
