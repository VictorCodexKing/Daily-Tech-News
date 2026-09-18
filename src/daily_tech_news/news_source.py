"""Fetch and parse technology news headlines from an RSS/Atom feed."""

from __future__ import annotations

from dataclasses import dataclass

import feedparser
import requests

DEFAULT_FEED_URL = "https://hnrss.org/frontpage"
DEFAULT_TIMEOUT = 15
USER_AGENT = "daily-tech-news/0.1 (+https://github.com/VictorCodexKing/Daily-Tech-News)"


class NewsFetchError(Exception):
    """Raised when headlines cannot be fetched or parsed."""


@dataclass
class Headline:
    """A single news headline."""

    title: str
    url: str
    source: str
    published: str | None = None


def parse_feed(content: str, source: str, limit: int) -> list[Headline]:
    """Parse raw feed ``content`` into a list of :class:`Headline` objects.

    This is separated from network access so it can be unit-tested offline.
    Raises :class:`NewsFetchError` if the content cannot be parsed into any
    usable entries.
    """
    if limit < 0:
        raise NewsFetchError("limit must be non-negative")

    parsed = feedparser.parse(content)

    if parsed.bozo and not parsed.entries:
        reason = getattr(parsed, "bozo_exception", "unknown parse error")
        raise NewsFetchError(f"Failed to parse feed content: {reason}")

    headlines: list[Headline] = []
    for entry in parsed.entries[:limit]:
        title = getattr(entry, "title", "").strip()
        url = getattr(entry, "link", "").strip()
        if not title or not url:
            continue
        published = getattr(entry, "published", None)
        headlines.append(
            Headline(title=title, url=url, source=source, published=published)
        )

    return headlines


def fetch_headlines(
    limit: int = 10, feed_url: str = DEFAULT_FEED_URL
) -> list[Headline]:
    """Fetch the feed at ``feed_url`` and return up to ``limit`` headlines.

    Raises :class:`NewsFetchError` on any network or parse failure.
    """
    try:
        response = requests.get(
            feed_url,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise NewsFetchError(f"Could not fetch feed from {feed_url}: {exc}") from exc

    return parse_feed(response.text, source=feed_url, limit=limit)
