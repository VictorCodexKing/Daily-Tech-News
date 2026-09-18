"""Format headlines into a Telegram HTML-parse-mode message."""

from __future__ import annotations

from datetime import date
from html import escape

from .news_source import Headline


def format_message(headlines: list[Headline]) -> str:
    """Render ``headlines`` as a dated Telegram HTML message.

    Each headline becomes a numbered clickable link. Titles are HTML-escaped
    so that special characters (``&``, ``<``, ``>``) are safe under Telegram's
    HTML parse mode. An empty list yields a friendly "no headlines" message.
    """
    today = date.today().strftime("%B %d, %Y")
    header = f"<b>\U0001f4f0 Daily Tech News \u2014 {escape(today)}</b>"

    if not headlines:
        return f"{header}\n\nNo headlines available today."

    lines = [header, ""]
    for index, headline in enumerate(headlines, start=1):
        safe_title = escape(headline.title)
        safe_url = escape(headline.url, quote=True)
        lines.append(f'{index}. <a href="{safe_url}">{safe_title}</a>')

    return "\n".join(lines)
