from tools.mcp_client import run_mcp_tool


def get_hotels(location: str):
    return run_mcp_tool(
        "mcp_server/hotel_server.py",
        "search_hotels",
        {"location": location},
    )
