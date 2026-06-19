import asyncio
import json

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tools.mcp_config import mcp_server_params


async def call_mcp_tool(server_script: str, tool_name: str, arguments: dict):
    server_params = mcp_server_params(server_script)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return [json.loads(item.text) for item in result.content]


def run_mcp_tool(server_script: str, tool_name: str, arguments: dict):
    return asyncio.run(call_mcp_tool(server_script, tool_name, arguments))
