"""Configuration loading and validation.

Credentials are read only from the environment (optionally seeded from a
``.env`` file). Nothing is ever hardcoded.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass
class Config:
    """Runtime configuration required to send messages to Telegram."""

    bot_token: str
    chat_id: str


def load_config() -> Config:
    """Load and validate Telegram credentials from the environment.

    A ``.env`` file in the current working directory (or any parent) is loaded
    first, if present. Raises :class:`ConfigError` naming every missing
    variable, rather than a raw ``KeyError``.
    """
    load_dotenv()

    bot_token = os.environ.get(BOT_TOKEN_ENV, "").strip()
    chat_id = os.environ.get(CHAT_ID_ENV, "").strip()

    missing = []
    if not bot_token:
        missing.append(BOT_TOKEN_ENV)
    if not chat_id:
        missing.append(CHAT_ID_ENV)

    if missing:
        raise ConfigError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Set them in your environment or a .env file."
        )

    return Config(bot_token=bot_token, chat_id=chat_id)
