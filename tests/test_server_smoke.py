import asyncio
import json

from okta_auth import server
from okta_auth.credential_store import StoredCredentials


def test_server_exports_tools() -> None:
    expected = [
        "okta_login",
        "okta_check_session",
        "okta_list_sessions",
        "okta_delete_session",
        "okta_get_cookies",
        "main",
    ]
    for name in expected:
        assert hasattr(server, name)


def test_okta_login_uses_stored_credentials(monkeypatch) -> None:
    async def fake_perform_login(**kwargs):
        assert kwargs["username"] == "user@example.com"
        assert kwargs["password"] == "secret"
        assert kwargs["totp_secret"] == "JBSWY3DPEHPK3PXP"
        return {"success": True, "url": kwargs["url"], "message": "ok", "domain_key": "example.com"}

    monkeypatch.setattr(server, "perform_login", fake_perform_login)
    monkeypatch.setattr(
        server,
        "load_stored_credentials",
        lambda: StoredCredentials(
            username="user@example.com",
            password="secret",
            totp_secret="JBSWY3DPEHPK3PXP",
        ),
    )

    payload = json.loads(asyncio.run(server.okta_login(url="https://portal.example.com")))

    assert payload["success"] is True
