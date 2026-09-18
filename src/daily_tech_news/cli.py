"""Command-line interface orchestrating fetch -> format -> send."""

from __future__ import annotations

import argparse
import sys

from .config import ConfigError, load_config
from .formatter import format_message
from .news_source import DEFAULT_FEED_URL, NewsFetchError, fetch_headlines
from .telegram_client import TelegramError, send_message

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_CONFIG_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="daily-tech-news",
        description="Scrape daily technology news headlines and send them to Telegram.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of headlines to include (default: 10).",
    )
    parser.add_argument(
        "--feed-url",
        default=DEFAULT_FEED_URL,
        help=f"RSS/Atom feed URL to scrape (default: {DEFAULT_FEED_URL}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and format headlines and print them; do not send to Telegram "
        "and do not require credentials.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        headlines = fetch_headlines(limit=args.limit, feed_url=args.feed_url)
    except NewsFetchError as exc:
        print(f"Error fetching headlines: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    message = format_message(headlines)

    if args.dry_run:
        print(message)
        return EXIT_OK

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return EXIT_CONFIG_ERROR

    try:
        send_message(
            bot_token=config.bot_token,
            chat_id=config.chat_id,
            text=message,
        )
    except TelegramError as exc:
        print(f"Error sending message: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    print(f"Sent {len(headlines)} headline(s) to Telegram.")
    return EXIT_OK
