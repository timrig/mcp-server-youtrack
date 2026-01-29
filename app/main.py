from __future__ import annotations

import argparse
import os
from pathlib import Path

import anyio
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP


def _require_env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name, default)
    if not v:
        raise RuntimeError(f"Missing environment variable: {name}")
    return v

async def make_request(url, headers):
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

def build_mcp() -> FastMCP:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    token = _require_env("PERMANENT_TOKEN")
    base_url = _require_env("BASE_URL")

    mcp = FastMCP("Youtrack")

    @mcp.tool()
    async def youtrack_read(type: str):
        """Sucht und liest Daten in Youtrack\n"""
        """- type ist der Typ des angefragten Inhalts zu setzen. Setze z.B. issues, activities, articles etc."""

        headers = {"Authorization": f"Bearer {token}"}

        url = f"{base_url}{type}?fields=id,summary,project(name)"

        return await make_request(url, headers)

    return mcp

async def _run_stdio(mcp: FastMCP) -> None:
    await mcp.run_stdio_async()

async def _run_http(mcp: FastMCP, host: str, port: int) -> None:
    import uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host=host, port=port)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()

    mcp = build_mcp()

    if args.transport == "stdio":
        anyio.run(_run_stdio, mcp)
    else:
        anyio.run(_run_http, mcp, args.host, args.port)

if __name__ == "__main__":
    main()
