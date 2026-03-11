# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

okta-auth is an Okta login toolkit with an interactive CLI and an MCP server for session reuse. It uses Playwright to automate Okta SSO and persists per-domain session state for reuse by AI agents.

## Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e '.[dev]'
playwright install chromium

# Quality gates (run all three before submitting)
ruff format --check .
ruff check .
pytest

# Run single test
pytest tests/test_session_store.py -v

# Run interactive CLI
okta

# Run MCP server (stdio transport, stdout is JSON-RPC)
okta-auth
```

## Architecture

```
src/okta_auth/
├── server.py          # FastMCP entry point, defines all 5 MCP tools
├── log.py             # Stderr-only logging (stdout reserved for JSON-RPC)
├── auth/
│   ├── login.py       # auto_login() engine: selector-based form filling, portal detection, MFA/TOTP
│   ├── session_store.py  # Per-domain session CRUD at ~/.okta-auth/sessions/
│   └── totp.py        # pyotp wrapper for TOTP code generation
└── browser/
    ├── controller.py  # BrowserController async context manager, BrowserConfig dataclass
    ├── detection.py   # Cross-platform browser executable discovery with env var overrides
    └── helpers.py     # fill_first_match(), click_first_match(), maybe_switch_to_code_factor()
```

### Key Patterns

- **Selector redundancy**: `login.py` defines 16+ CSS selectors per form field (USERNAME_SELECTORS, PASSWORD_SELECTORS, etc.) tried in priority order for broad Okta form compatibility.
- **Portal detection**: `_is_on_portal()` confirms auth completion by checking domain change + login field absence.
- **Session keying**: Sessions are stored as `{domain_hash}.json` + `{domain_hash}.meta.json` using the URL's netloc as the domain key.
- **Async-first**: All I/O uses `async/await`; the server runs on asyncio via FastMCP.
- **Browser fallback**: `BrowserController` tries the requested channel first, falls back to default Chromium on launch failure.

## Code Style

- **Formatter/Linter**: Ruff (line-length 100, target py311, double quotes, LF endings)
- **Lint rules**: E, F, I (isort), B (flake8-bugbear); E501 ignored
- **Type checking**: mypy with `check_untyped_defs = true`, `ignore_missing_imports = true`
- **All logs go to stderr** — never print to stdout (breaks MCP stdio transport)
