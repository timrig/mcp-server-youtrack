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

async def make_get_request(endpoint: str, params: str):
    token = _require_env("PERMANENT_TOKEN")
    base_url = _require_env("BASE_URL")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}{endpoint}?{params}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
    
async def make_post_request(endpoint: str, payload: dict[str, str]):
    token = _require_env("PERMANENT_TOKEN")
    base_url = _require_env("BASE_URL")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}{endpoint}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

def build_mcp() -> FastMCP:
    """
    YouTrack ist eine Webanwendung zur Fehlerverwaltung und Projektmanagement.\n
    Sie bietet Funktionen wie Aufgabenverwaltung, Zeiterfassung, Agile-Boards und Berichterstattung.
    """

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    mcp = FastMCP("Youtrack")

    @mcp.tool()
    async def read_issues():
        """Sucht nach Fehlern in Youtrack"""
        return await make_get_request(endpoint = "issues", params = "fields=id,summary,description,created")
    
    @mcp.tool()
    async def read_articles():
        """Sucht nach Artikeln in Youtrack"""
        return await make_get_request(endpoint = "articles", params = "fields=hasStar,content,created,updated,id,idReadable,reporter(name),summary,project(shortName),content")
    
    @mcp.tool()
    async def read_projects():
        """Sucht nach Projekten in Youtrack"""
        return await make_get_request(endpoint = "admin/projects", params = "fields=id,name,shortName")
    
    @mcp.tool()
    async def set_new_issue(project_id: str, summary: str, description: str):
        """
        Erstellt für ein Projekt einen neuen Fehler.\n
        Falls der User keine project_id oder project_name angibt, muss diese zuvor ermittelt oder abgefragt werden.
        """
        payload = {
            "project": {"id": project_id},
            "summary": summary,
            "description": description
        }
        return await make_post_request(endpoint = "issues", payload = payload)

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
