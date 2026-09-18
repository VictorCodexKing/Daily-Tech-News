"""Tests for the Telegram Bot API client (POST mocked, no live network)."""

from __future__ import annotations

from unittest import mock

import pytest
import requests

from daily_tech_news import telegram_client
from daily_tech_news.telegram_client import (
    API_BASE,
    TelegramError,
    send_message,
)

TOKEN = "123456:SECRET-TOKEN-VALUE"
CHAT_ID = "987654"


def _ok_response():
    resp = mock.Mock()
    resp.status_code = 200
    resp.json = mock.Mock(return_value={"ok": True, "result": {"message_id": 42}})
    return resp


def test_send_message_posts_correct_url_and_payload():
    resp = _ok_response()
    with mock.patch.object(
        telegram_client.requests, "post", return_value=resp
    ) as mock_post:
        result = send_message(TOKEN, CHAT_ID, "hello world")

    assert result == {"message_id": 42}
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args

    expected_url = f"{API_BASE}/bot{TOKEN}/sendMessage"
    assert args[0] == expected_url

    payload = kwargs["json"]
    assert payload["chat_id"] == CHAT_ID
    assert payload["text"] == "hello world"
    assert payload["parse_mode"] == "HTML"
    assert payload["disable_web_page_preview"] is True
    assert "timeout" in kwargs


def test_send_message_respects_custom_parse_and_preview():
    resp = _ok_response()
    with mock.patch.object(
        telegram_client.requests, "post", return_value=resp
    ) as mock_post:
        send_message(
            TOKEN,
            CHAT_ID,
            "text",
            parse_mode="MarkdownV2",
            disable_web_page_preview=False,
        )

    payload = mock_post.call_args.kwargs["json"]
    assert payload["parse_mode"] == "MarkdownV2"
    assert payload["disable_web_page_preview"] is False


def test_send_message_ok_false_raises_and_hides_token():
    resp = mock.Mock()
    resp.status_code = 400
    resp.json = mock.Mock(
        return_value={"ok": False, "description": "Bad Request: chat not found"}
    )
    with mock.patch.object(telegram_client.requests, "post", return_value=resp):
        with pytest.raises(TelegramError) as excinfo:
            send_message(TOKEN, CHAT_ID, "text")

    message = str(excinfo.value)
    assert "chat not found" in message
    assert TOKEN not in message


def test_send_message_network_error_raises_telegramerror():
    with mock.patch.object(
        telegram_client.requests,
        "post",
        side_effect=requests.ConnectionError("connection refused"),
    ):
        with pytest.raises(TelegramError) as excinfo:
            send_message(TOKEN, CHAT_ID, "text")

    # The client surfaces network failures as TelegramError and does not
    # embed the bot token in its own message.
    assert TOKEN not in str(excinfo.value)


def test_send_message_invalid_json_raises_and_hides_token():
    resp = mock.Mock()
    resp.status_code = 502
    resp.json = mock.Mock(side_effect=ValueError("no json"))
    with mock.patch.object(telegram_client.requests, "post", return_value=resp):
        with pytest.raises(TelegramError) as excinfo:
            send_message(TOKEN, CHAT_ID, "text")

    assert TOKEN not in str(excinfo.value)
