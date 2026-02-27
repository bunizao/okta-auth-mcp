"""Minimal stderr logger for MCP server context.

MCP stdio transport uses stdout for JSON-RPC — all logging MUST go to stderr.
"""

import logging
import sys

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

logger = logging.getLogger("okta_auth_mcp")
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


def debug_detail(message: str) -> None:
    logger.debug(message)
