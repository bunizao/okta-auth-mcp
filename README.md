# okta-auth-mcp

MCP server that performs Okta SSO login through Playwright and persists per-domain session state for reuse by AI agents.

## What It Provides

- `okta_login`: authenticate to a target URL and store session state
- `okta_check_session`: verify whether a stored session is still valid
- `okta_list_sessions`: list saved sessions and metadata
- `okta_delete_session`: remove a stored session
- `okta_get_cookies`: retrieve cookies from stored session (sensitive)

Sessions are stored under `~/.okta-auth-mcp/sessions/`.

## Security Model

- This server is intended for **local trusted execution**.
- Session files and cookies are sensitive credentials; protect the host account.
- Prefer private/internal usage unless security controls are reviewed.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e '.[dev]'
python -m playwright install chromium
```

Run server over stdio:

```bash
okta-auth-mcp
```

## MCP Client Config Example

```json
{
  "mcpServers": {
    "okta-auth": {
      "command": "okta-auth-mcp",
      "args": []
    }
  }
}
```

## Development

Run checks locally:

```bash
ruff format --check .
ruff check .
pytest
```

## Release

- Tag format: `vX.Y.Z`
- GitHub Actions builds distributions and publishes to PyPI with trusted publishing.
- Configure PyPI trusted publisher to enable release workflow.
