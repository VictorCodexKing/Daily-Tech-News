"""Tests for configuration loading and validation."""

from __future__ import annotations

import pytest

from daily_tech_news import config as config_module
from daily_tech_news.config import (
    BOT_TOKEN_ENV,
    CHAT_ID_ENV,
    Config,
    ConfigError,
    load_config,
)


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch):
    """Prevent load_config from reading a real .env file during tests."""
    monkeypatch.setattr(config_module, "load_dotenv", lambda *a, **k: False)


def test_load_config_returns_config_when_both_set(monkeypatch):
    monkeypatch.setenv(BOT_TOKEN_ENV, "token-123")
    monkeypatch.setenv(CHAT_ID_ENV, "chat-456")

    cfg = load_config()

    assert isinstance(cfg, Config)
    assert cfg.bot_token == "token-123"
    assert cfg.chat_id == "chat-456"


def test_load_config_raises_naming_both_missing(monkeypatch):
    monkeypatch.delenv(BOT_TOKEN_ENV, raising=False)
    monkeypatch.delenv(CHAT_ID_ENV, raising=False)

    with pytest.raises(ConfigError) as excinfo:
        load_config()

    message = str(excinfo.value)
    assert BOT_TOKEN_ENV in message
    assert CHAT_ID_ENV in message


def test_load_config_raises_naming_missing_token_only(monkeypatch):
    monkeypatch.delenv(BOT_TOKEN_ENV, raising=False)
    monkeypatch.setenv(CHAT_ID_ENV, "chat-456")

    with pytest.raises(ConfigError) as excinfo:
        load_config()

    message = str(excinfo.value)
    assert BOT_TOKEN_ENV in message
    assert CHAT_ID_ENV not in message


def test_load_config_raises_naming_missing_chat_id_only(monkeypatch):
    monkeypatch.setenv(BOT_TOKEN_ENV, "token-123")
    monkeypatch.delenv(CHAT_ID_ENV, raising=False)

    with pytest.raises(ConfigError) as excinfo:
        load_config()

    message = str(excinfo.value)
    assert CHAT_ID_ENV in message
    assert BOT_TOKEN_ENV not in message
