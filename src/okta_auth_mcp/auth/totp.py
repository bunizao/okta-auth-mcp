"""TOTP generation for automated MFA."""

import pyotp


def gen_totp(secret: str) -> str:
    """Generate a TOTP code from a base32 shared secret."""
    return pyotp.TOTP(secret).now()
