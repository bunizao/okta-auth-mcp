# Contributing

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e '.[dev]'
python -m playwright install chromium
```

## Local Quality Gates

```bash
ruff format --check .
ruff check .
pytest
```

## Pull Requests

- Keep PRs focused and small.
- Add/update tests for behavior changes.
- Do not commit secrets, cookies, or local session files.
