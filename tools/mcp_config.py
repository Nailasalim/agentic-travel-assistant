"""Shared MCP client configuration."""

import os
import sys
from pathlib import Path

from mcp import StdioServerParameters

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def mcp_server_params(server_script: str) -> StdioServerParameters:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{pythonpath}" if pythonpath else str(PROJECT_ROOT)
    )

    script_path = PROJECT_ROOT / server_script

    return StdioServerParameters(
        command=sys.executable,
        args=[str(script_path)],
        env=env,
        cwd=str(PROJECT_ROOT),
    )
