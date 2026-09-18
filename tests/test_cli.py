"""Tests for CLI orchestration (fetch/send patched, no live network)."""

from __future__ import annotations

from unittest import mock

from daily_tech_news import cli
from daily_tech_news.cli import (
    EXIT_CONFIG_ERROR,
    EXIT_OK,
    main,
)
from daily_tech_news.config import ConfigError
from daily_tech_news.news_source import Headline


def _headlines():
    return [Headline(title="Alpha", url="https://example.com/a", source="src")]


def test_dry_run_prints_and_returns_ok_without_send(capsys):
    with mock.patch.object(
        cli, "fetch_headlines", return_value=_headlines()
    ) as mock_fetch, mock.patch.object(cli, "send_message") as mock_send, mock.patch.object(
        cli, "load_config"
    ) as mock_config:
        rc = main(["--dry-run", "--limit", "5"])

    assert rc == EXIT_OK
    mock_fetch.assert_called_once()
    # Dry run must neither send nor require credentials.
    mock_send.assert_not_called()
    mock_config.assert_not_called()

    out = capsys.readouterr().out
    assert "Alpha" in out


def test_normal_path_calls_send_once_and_returns_ok():
    fake_config = mock.Mock(bot_token="token", chat_id="chat")
    with mock.patch.object(
        cli, "fetch_headlines", return_value=_headlines()
    ), mock.patch.object(
        cli, "load_config", return_value=fake_config
    ), mock.patch.object(cli, "send_message") as mock_send:
        rc = main([])

    assert rc == EXIT_OK
    mock_send.assert_called_once()


def test_missing_credentials_returns_config_exit_code(capsys):
    with mock.patch.object(
        cli, "fetch_headlines", return_value=_headlines()
    ), mock.patch.object(
        cli, "load_config", side_effect=ConfigError("Missing TELEGRAM_BOT_TOKEN")
    ), mock.patch.object(cli, "send_message") as mock_send:
        rc = main([])

    assert rc == EXIT_CONFIG_ERROR
    mock_send.assert_not_called()
    err = capsys.readouterr().err
    assert "Missing TELEGRAM_BOT_TOKEN" in err
