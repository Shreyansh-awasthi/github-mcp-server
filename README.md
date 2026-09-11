# GitHub MCP Server

A Model Context Protocol (MCP) server that exposes GitHub functionality
(repositories, issues, pull requests, file contents, code search, branches,
commits) as tools for MCP-compatible clients like Claude Code.

## Requirements

- Python 3.10+
- A GitHub Personal Access Token

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install mcp requests
```

Create a GitHub token at https://github.com/settings/tokens with `repo` scope
(or read-only Contents/Issues/Pull requests for a read-only server).

## Connect to Claude Code

```powershell
claude mcp add github -- "path\to\.venv\Scripts\python.exe" "path\to\github_server_mcp.py"
```

Then add your token to the `env` field in `.claude.json` for this server entry:

```json
"env": { "GITHUB_TOKEN": "your_token_here" }
```

Verify:
```powershell
claude mcp list
```

## Available tools

| Tool | Description |
|---|---|
| `search_repositories` | Search repos by keyword/query |
| `get_repository` | Get metadata for one repo |
| `list_issues` | List issues in a repo |
| `get_issue` | Get a single issue |
| `create_issue` | Create a new issue |
| `add_issue_comment` | Comment on an issue or PR |
| `list_pull_requests` | List PRs in a repo |
| `get_pull_request` | Get a single PR |
| `create_pull_request` | Open a new PR |
| `get_file_contents` | Read a file or list a directory |
| `search_code` | Search code across GitHub |
| `list_branches` | List branches in a repo |
| `list_commits` | List commits on a branch/ref |

## Notes

- Never commit your `GITHUB_TOKEN` — it should only live in your local
  `.claude.json` env config, not in this repo.
- Without a token, only unauthenticated (public, rate-limited) access works.
