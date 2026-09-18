"""Tests for the Telegram message formatter."""

from __future__ import annotations

from datetime import date

from daily_tech_news.formatter import format_message
from daily_tech_news.news_source import Headline


def _sample_headlines():
    return [
        Headline(title="Alpha release", url="https://example.com/a", source="src"),
        Headline(title="Beta news", url="https://example.com/b", source="src"),
    ]


def test_format_message_includes_date_header():
    message = format_message(_sample_headlines())
    today = date.today().strftime("%B %d, %Y")
    assert today in message
    # Header is bold.
    assert "<b>" in message and "</b>" in message


def test_format_message_numbers_items_and_emits_links():
    message = format_message(_sample_headlines())
    lines = message.splitlines()

    assert '1. <a href="https://example.com/a">Alpha release</a>' in lines
    assert '2. <a href="https://example.com/b">Beta news</a>' in lines


def test_format_message_escapes_html_in_titles():
    headlines = [
        Headline(
            title="Rust & Go <beat> C",
            url="https://example.com/x?a=1&b=2",
            source="src",
        )
    ]
    message = format_message(headlines)

    # The raw special characters must not appear un-escaped in the title.
    assert "Rust & Go <beat> C" not in message
    assert "Rust &amp; Go &lt;beat&gt; C" in message
    # The URL ampersand is escaped too.
    assert "a=1&amp;b=2" in message


def test_format_message_empty_list():
    message = format_message([])
    assert "No headlines" in message
    # Still dated, still has a header.
    today = date.today().strftime("%B %d, %Y")
    assert today in message
    # No numbered link entries.
    assert "<a href=" not in message
