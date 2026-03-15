from okta_auth import config_wizard
from okta_auth.credential_store import StoredCredentials
from okta_auth.settings import AppSettings


class _TTY:
    def isatty(self) -> bool:
        return True


def test_config_wizard_saves_credentials_and_settings(monkeypatch) -> None:
    inputs = iter(
        [
            "",
            "https://portal.example.com",
            "user@example.com",
            "JBSW Y3DP EHPK 3PXP",
            "y",
        ]
    )
    secret_inputs = iter(["super-secret-password"])
    saved = {}

    wizard = config_wizard.ConfigWizard(
        input_func=lambda prompt="": next(inputs),
        secret_input_func=lambda prompt="": next(secret_inputs),
        print_func=lambda *args, **kwargs: None,
        stdin=_TTY(),
        stdout=_TTY(),
    )

    monkeypatch.setattr(
        config_wizard.credential_store,
        "get_store_status",
        lambda: {"available": True, "backend": "FakeKeyring", "error": None},
    )
    monkeypatch.setattr(
        config_wizard.credential_store,
        "load_credentials",
        lambda: StoredCredentials(
            username="old@example.com",
            password="old-password",
            totp_secret="OLDSECRET",
        ),
    )
    monkeypatch.setattr(
        config_wizard.settings,
        "load_settings",
        lambda: AppSettings(default_url="https://old.example.com"),
    )
    monkeypatch.setattr(
        config_wizard.credential_store,
        "save_credentials",
        lambda username, password, totp_secret: saved.update(
            {
                "username": username,
                "password": password,
                "totp_secret": totp_secret,
            }
        ),
    )
    monkeypatch.setattr(
        config_wizard.settings,
        "save_settings",
        lambda app_settings: (
            saved.update({"default_url": app_settings.default_url}) or "/tmp/config.json"
        ),
    )

    exit_code = wizard.run()

    assert exit_code == 0
    assert saved == {
        "username": "user@example.com",
        "password": "super-secret-password",
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "default_url": "https://portal.example.com",
    }
