import base64
import json
import os
import sys
from typing import Any

import requests
from mcp.server.mcpserver import MCPServer

GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN")

mcp = MCPServer("github-mcp-server")


def _headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-mcp-server/1.0",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def _request(method: str, path: str, params: dict | None = None,
             json_body: dict | None = None) -> Any:
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    resp = requests.request(
        method, url, headers=_headers(), params=params, json=json_body, timeout=30
    )
    if resp.status_code >= 400:
        raise RuntimeError(
            f"GitHub API error {resp.status_code} for {method} {url}: {resp.text[:500]}"
        )
    if resp.text:
        return resp.json()
    return None


def _dump(payload: Any) -> str:
    if isinstance(payload, (dict, list)):
        return json.dumps(payload, indent=2)
    return str(payload)


@mcp.tool()
def search_repositories(query: str, per_page: int = 10) -> str:
    data = _request("GET", "/search/repositories", params={"q": query, "per_page": per_page})
    return _dump(data)


@mcp.tool()
def get_repository(owner: str, repo: str) -> str:
    data = _request("GET", f"/repos/{owner}/{repo}")
    return _dump(data)


@mcp.tool()
def list_issues(owner: str, repo: str, state: str = "open", per_page: int = 20) -> str:
    data = _request(
        "GET", f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": per_page},
    )
    return _dump(data)


@mcp.tool()
def get_issue(owner: str, repo: str, issue_number: int) -> str:
    data = _request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
    return _dump(data)


@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: str = "",
                  labels: list[str] | None = None) -> str:
    payload: dict[str, Any] = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    data = _request("POST", f"/repos/{owner}/{repo}/issues", json_body=payload)
    return _dump(data)


@mcp.tool()
def add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> str:
    data = _request(
        "POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
        json_body={"body": body},
    )
    return _dump(data)


@mcp.tool()
def list_pull_requests(owner: str, repo: str, state: str = "open", per_page: int = 20) -> str:
    data = _request(
        "GET", f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "per_page": per_page},
    )
    return _dump(data)


@mcp.tool()
def get_pull_request(owner: str, repo: str, pull_number: int) -> str:
    data = _request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}")
    return _dump(data)


@mcp.tool()
def create_pull_request(owner: str, repo: str, title: str, head: str, base: str,
                         body: str = "", draft: bool = False) -> str:
    payload = {"title": title, "head": head, "base": base, "body": body, "draft": draft}
    data = _request("POST", f"/repos/{owner}/{repo}/pulls", json_body=payload)
    return _dump(data)


@mcp.tool()
def get_file_contents(owner: str, repo: str, path: str, ref: str | None = None) -> str:
    params = {"ref": ref} if ref else {}
    data = _request("GET", f"/repos/{owner}/{repo}/contents/{path}", params=params)
    if isinstance(data, dict) and data.get("encoding") == "base64":
        try:
            decoded = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return _dump({"path": data.get("path"), "sha": data.get("sha"), "content": decoded})
        except Exception:
            pass
    return _dump(data)


@mcp.tool()
def search_code(query: str, per_page: int = 10) -> str:
    data = _request("GET", "/search/code", params={"q": query, "per_page": per_page})
    return _dump(data)


@mcp.tool()
def list_branches(owner: str, repo: str, per_page: int = 30) -> str:
    data = _request("GET", f"/repos/{owner}/{repo}/branches", params={"per_page": per_page})
    return _dump(data)


@mcp.tool()
def list_commits(owner: str, repo: str, sha: str | None = None, per_page: int = 20) -> str:
    params: dict[str, Any] = {"per_page": per_page}
    if sha:
        params["sha"] = sha
    data = _request("GET", f"/repos/{owner}/{repo}/commits", params=params)
    return _dump(data)


def run():
    if not TOKEN:
        print(
            "Warning: GITHUB_TOKEN not set. Only unauthenticated (public, "
            "rate-limited) GitHub API access will work.",
            file=sys.stderr,
        )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()