"""Tests for feed parsing and headline fetching (no live network)."""

from __future__ import annotations

from unittest import mock

import pytest
import requests

from daily_tech_news import news_source
from daily_tech_news.news_source import (
    Headline,
    NewsFetchError,
    fetch_headlines,
    parse_feed,
)

from .fixtures import MALFORMED_FEED, SAMPLE_RSS


def test_parse_feed_returns_expected_headlines():
    headlines = parse_feed(SAMPLE_RSS, source="https://example.com/feed", limit=10)

    assert len(headlines) == 3
    assert all(isinstance(h, Headline) for h in headlines)

    first = headlines[0]
    # feedparser unescapes entities, so the raw title characters are present.
    assert first.title == "First headline about Rust & Go"
    assert first.url == "https://example.com/articles/1"
    assert first.source == "https://example.com/feed"
    assert first.published is not None

    assert headlines[1].title == "Second headline <breaking>"
    assert headlines[2].url == "https://example.com/articles/3"


def test_parse_feed_respects_limit():
    headlines = parse_feed(SAMPLE_RSS, source="src", limit=2)
    assert len(headlines) == 2
    assert headlines[0].url == "https://example.com/articles/1"
    assert headlines[1].url == "https://example.com/articles/2"


def test_parse_feed_malformed_raises():
    with pytest.raises(NewsFetchError):
        parse_feed(MALFORMED_FEED, source="src", limit=5)


def test_fetch_headlines_mocked_success():
    fake_response = mock.Mock()
    fake_response.text = SAMPLE_RSS
    fake_response.raise_for_status = mock.Mock()

    with mock.patch.object(
        news_source.requests, "get", return_value=fake_response
    ) as mock_get:
        headlines = fetch_headlines(limit=2, feed_url="https://example.com/feed")

    assert len(headlines) == 2
    assert headlines[0].source == "https://example.com/feed"

    # Assert the request was made with a User-Agent header and a timeout.
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert kwargs["timeout"] == news_source.DEFAULT_TIMEOUT
    assert "User-Agent" in kwargs["headers"]
    assert kwargs["headers"]["User-Agent"] == news_source.USER_AGENT


def test_fetch_headlines_network_error_becomes_newsfetcherror():
    with mock.patch.object(
        news_source.requests,
        "get",
        side_effect=requests.ConnectionError("boom"),
    ):
        with pytest.raises(NewsFetchError):
            fetch_headlines(limit=5, feed_url="https://example.com/feed")


def test_fetch_headlines_http_error_becomes_newsfetcherror():
    fake_response = mock.Mock()
    fake_response.raise_for_status = mock.Mock(
        side_effect=requests.HTTPError("500 Server Error")
    )

    with mock.patch.object(news_source.requests, "get", return_value=fake_response):
        with pytest.raises(NewsFetchError):
            fetch_headlines(limit=5, feed_url="https://example.com/feed")
