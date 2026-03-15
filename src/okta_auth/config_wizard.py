"""Interactive terminal wizard for configuring local credentials."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Callable
from urllib.parse import urlparse

from okta_auth import credential_store, settings

InputFunc = Callable[[str], str]
SecretInputFunc = Callable[[str], str]
PrintFunc = Callable[..., None]


@dataclass
class WizardState:
    default_url: str | None
    username: str | None
    password: str | None
    totp_secret: str | None
    password_stored: bool
    totp_secret_stored: bool
    keyring_backend: str


class ConfigWizard:
    """Small step-based TUI wizard that stores secrets in the OS keyring."""

    def __init__(
        self,
        *,
        input_func: InputFunc = input,
        secret_input_func: SecretInputFunc = getpass,
        print_func: PrintFunc = print,
        stdin: object = sys.stdin,
        stdout: object = sys.stdout,
    ) -> None:
        self._input = input_func
        self._secret_input = secret_input_func
        self._print = print_func
        self._stdin = stdin
        self._stdout = stdout

    def run(self) -> int:
        """Collect configuration interactively and save it."""
        if not self._is_tty():
            print("`okta config` requires an interactive terminal.", file=sys.stderr)
            return 1

        status = credential_store.get_store_status()
        if not status["available"]:
            print(f"OS keyring is unavailable: {status['error']}", file=sys.stderr)
            return 1

        state = self._load_state(status)
        self._show_step(
            1,
            6,
            "Welcome",
            [
                "This wizard stores your Okta credentials in the OS keyring.",
                "Only the default portal URL is written to ~/.okta-auth/config.json.",
                "Leave a field blank to keep the current value.",
                "Type `none` for the TOTP secret to remove it.",
            ],
        )
        self._input("Press Enter to continue...")

        state.default_url = self._prompt_default_url(state.default_url)
        state.username = self._prompt_username(state.username)
        state.password = self._prompt_password(state.password_stored)
        state.totp_secret = self._prompt_totp_secret(state.totp_secret, state.totp_secret_stored)

        self._show_review(state)
        confirm = self._input("Save this configuration? [Y/n]: ").strip().lower()
        if confirm not in {"", "y", "yes"}:
            self._print("Configuration was not changed.")
            return 1

        credential_store.save_credentials(
            username=state.username or "",
            password=state.password or "",
            totp_secret=state.totp_secret,
        )
        settings_path = settings.save_settings(settings.AppSettings(default_url=state.default_url))
        self._print("")
        self._print("Configuration saved.")
        self._print(f"Secrets: OS keyring ({state.keyring_backend})")
        self._print(f"Settings: {settings_path}")
        return 0

    def _is_tty(self) -> bool:
        return bool(getattr(self._stdin, "isatty", lambda: False)()) and bool(
            getattr(self._stdout, "isatty", lambda: False)()
        )

    def _load_state(self, status: dict[str, object]) -> WizardState:
        stored = credential_store.load_credentials()
        app_settings = settings.load_settings()
        return WizardState(
            default_url=app_settings.default_url,
            username=stored.username,
            password=stored.password,
            totp_secret=stored.totp_secret,
            password_stored=bool(stored.password),
            totp_secret_stored=bool(stored.totp_secret),
            keyring_backend=str(status["backend"]),
        )

    def _prompt_default_url(self, current: str | None) -> str | None:
        self._show_step(
            2,
            6,
            "Default URL",
            [
                f"Current default URL: {current or '(not set)'}",
                "This value is optional and is used by `okta` when no URL argument is passed.",
                "Enter a full http(s) URL or type `none` to clear it.",
            ],
        )
        while True:
            entered = self._input("Default portal URL: ").strip()
            if not entered:
                return current
            if entered.lower() == "none":
                return None
            if _is_valid_url(entered):
                return entered
            self._print("Enter a full URL like https://portal.company.com.")

    def _prompt_username(self, current: str | None) -> str:
        self._show_step(
            3,
            6,
            "Username",
            [
                f"Current username: {current or '(not set)'}",
                "The username is stored in the OS keyring with your password.",
            ],
        )
        while True:
            entered = self._input("Okta username or email: ").strip()
            if entered:
                return entered
            if current:
                return current
            self._print("Username is required.")

    def _prompt_password(self, password_stored: bool) -> str:
        self._show_step(
            4,
            6,
            "Password",
            [
                f"Current password: {'stored' if password_stored else '(not set)'}",
                "The password is always written to the OS keyring, never to a local file.",
            ],
        )
        while True:
            entered = self._secret_input("Okta password: ").strip()
            if entered:
                return entered
            if password_stored:
                stored = credential_store.load_credentials()
                if stored.password:
                    return stored.password
            self._print("Password is required.")

    def _prompt_totp_secret(self, current: str | None, totp_secret_stored: bool) -> str | None:
        self._show_step(
            5,
            6,
            "TOTP",
            [
                f"Current TOTP secret: {'stored' if totp_secret_stored else '(not set)'}",
                "This field is optional. Leave it blank to keep the current value.",
                "Type `none` to remove the stored TOTP secret.",
            ],
        )
        entered = self._input("TOTP secret: ").strip()
        if not entered:
            return current
        if entered.lower() == "none":
            return None
        return entered.replace(" ", "").upper()

    def _show_review(self, state: WizardState) -> None:
        self._show_step(
            6,
            6,
            "Review",
            [
                f"Default URL: {state.default_url or '(not set)'}",
                f"Username: {state.username or '(not set)'}",
                "Password: stored in OS keyring",
                f"TOTP secret: {'stored' if state.totp_secret else '(not set)'}",
                f"Keyring backend: {state.keyring_backend}",
            ],
        )

    def _show_step(self, step: int, total: int, title: str, lines: list[str]) -> None:
        self._print("")
        self._print("=" * 64)
        self._print(f"Okta Config Wizard [{step}/{total}] - {title}")
        self._print("=" * 64)
        for line in lines:
            self._print(line)


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
