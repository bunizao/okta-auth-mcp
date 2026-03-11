import json
from pathlib import Path

from okta_auth import cli


def test_okta_defaults_to_login(monkeypatch, capsys) -> None:
    async def fake_perform_login(**kwargs):
        assert kwargs["url"] == "https://portal.example.com"
        assert kwargs["username"] == "user@example.com"
        assert kwargs["password"] == "secret"
        assert kwargs["totp_secret"] is None
        assert kwargs["headed"] is False
        return {
            "success": True,
            "domain_key": "portal.example.com",
            "message": "Session saved for portal.example.com",
            "url": "https://portal.example.com",
        }

    monkeypatch.setattr(cli, "perform_login", fake_perform_login)
    monkeypatch.setattr(cli.session_store, "get_session_path", lambda url: "/tmp/session.json")
    monkeypatch.setattr(cli.session_store, "SESSIONS_DIR", Path("/tmp/sessions"))

    exit_code = cli.main(
        [
            "https://portal.example.com",
            "--username",
            "user@example.com",
            "--password",
            "secret",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Session saved for portal.example.com" in output
    assert "Sensitive session data is stored locally under: /tmp/sessions" in output
    assert "Session file: /tmp/session.json" in output


def test_okta_login_can_enable_headed_mode(monkeypatch) -> None:
    async def fake_perform_login(**kwargs):
        assert kwargs["headed"] is True
        return {
            "success": True,
            "domain_key": "portal.example.com",
            "message": "Session saved for portal.example.com",
            "url": "https://portal.example.com",
        }

    monkeypatch.setattr(cli, "perform_login", fake_perform_login)
    monkeypatch.setattr(cli.session_store, "get_session_path", lambda url: None)

    exit_code = cli.main(
        [
            "https://portal.example.com",
            "--username",
            "user@example.com",
            "--password",
            "secret",
            "--headed",
        ]
    )

    assert exit_code == 0


def test_okta_check_json(monkeypatch, capsys) -> None:
    async def fake_verify_session(**kwargs):
        assert kwargs["url"] == "https://portal.example.com"
        return {
            "valid": True,
            "domain_key": "portal.example.com",
            "message": "Session is active",
            "url": "https://portal.example.com",
        }

    monkeypatch.setattr(cli, "verify_session", fake_verify_session)

    exit_code = cli.main(["check", "https://portal.example.com", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert payload["domain_key"] == "portal.example.com"
