"""Non-secret local settings for the CLI."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from okta_auth.auth.session_store import DATA_DIR

CONFIG_PATH = DATA_DIR / "config.json"


@dataclass
class AppSettings:
    default_url: str | None = None


def load_settings() -> AppSettings:
    """Load settings from disk. Invalid files are ignored."""
    if not CONFIG_PATH.exists():
        return AppSettings()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return AppSettings()

    default_url = data.get("default_url")
    if isinstance(default_url, str):
        default_url = default_url.strip() or None
    else:
        default_url = None

    return AppSettings(default_url=default_url)


def save_settings(settings: AppSettings) -> Path:
    """Persist non-secret settings under ~/.okta-auth."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(asdict(settings), file, indent=2)

    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass

    return CONFIG_PATH


def clear_settings() -> None:
    """Delete the local settings file when present."""
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()


def describe_settings() -> dict[str, object]:
    """Return non-sensitive settings metadata."""
    settings = load_settings()
    return {
        "config_exists": CONFIG_PATH.exists(),
        "config_path": str(CONFIG_PATH),
        "default_url": settings.default_url,
    }
