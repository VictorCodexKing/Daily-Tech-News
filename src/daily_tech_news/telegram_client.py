"""Minimal Telegram Bot API client for sending messages."""

from __future__ import annotations

import requests

API_BASE = "https://api.telegram.org"
DEFAULT_TIMEOUT = 15


class TelegramError(Exception):
    """Raised when a Telegram Bot API request fails.

    The bot token is never included in the message.
    """


def send_message(
    bot_token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> dict:
    """Send ``text`` to ``chat_id`` via the Telegram ``sendMessage`` method.

    Returns the parsed JSON ``result`` on success. Raises :class:`TelegramError`
    on network failure, an HTTP error, invalid JSON, or an ``ok=false`` response.
    The bot token is never logged or embedded in raised errors.
    """
    url = f"{API_BASE}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    try:
        response = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        raise TelegramError(f"Failed to reach the Telegram API: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise TelegramError(
            f"Telegram API returned invalid JSON (HTTP {response.status_code})."
        ) from exc

    if not data.get("ok", False):
        description = data.get("description", "unknown error")
        raise TelegramError(f"Telegram API error: {description}")

    return data.get("result", {})
