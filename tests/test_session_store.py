import json
from pathlib import Path

from okta_auth_mcp.auth import session_store


def _write_storage_state(
    path: Path, cookies: list | None = None, origins: list | None = None
) -> None:
    payload = {
        "cookies": cookies or [],
        "origins": origins or [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_save_get_list_delete_session(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(session_store, "SESSIONS_DIR", tmp_path / "sessions")

    source = tmp_path / "state.json"
    _write_storage_state(source, cookies=[{"name": "sid", "value": "abc"}])

    url = "https://portal.example.com/student"
    key = session_store.save_session(url, str(source))

    stored_path = session_store.get_session_path(url)
    assert stored_path is not None
    assert key == "portal.example.com"
    assert session_store.is_session_effective(url)

    sessions = session_store.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["domain_key"] == key
    assert sessions[0]["cookie_count"] == 1

    assert session_store.delete_session(url)
    assert session_store.get_session_path(url) is None
    assert not session_store.list_sessions()


def test_is_session_effective_handles_bad_json(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(session_store, "SESSIONS_DIR", tmp_path / "sessions")
    session_store.ensure_sessions_dir()

    broken = session_store.SESSIONS_DIR / "portal.example.com.json"
    broken.write_text("{bad json", encoding="utf-8")

    assert session_store.is_session_effective("https://portal.example.com") is False
