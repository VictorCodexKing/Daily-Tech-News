# Daily Tech News

Scrape daily technology news headlines from an RSS/Atom feed (Hacker News front
page by default) and deliver them to a Telegram chat via the Bot API.

## Features

- Fetches the latest headlines from a configurable RSS/Atom feed.
- Formats them as a dated, numbered message with clickable links (Telegram HTML
  parse mode), safely escaping special characters in titles.
- Sends the message to your Telegram chat using the Bot API.
- `--dry-run` mode prints the message locally without sending or requiring
  credentials, which is handy for previews and testing.
- Reads credentials only from the environment or a `.env` file; nothing is
  hardcoded.

## Requirements

- Python 3.10 or newer.
- A Telegram bot token and a chat ID (see below).

## Installation

### Using uv (recommended)

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .[dev]
```

### Using plain pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Omit `[dev]` if you only want the runtime dependencies (no test/lint tools).

## Getting a Telegram Bot Token

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to name your bot.
3. BotFather replies with an API token that looks like
   `123456789:AAExampleTokenValue`. Keep it secret.

## Finding your Chat ID

1. Send any message to your new bot (so it has a chat to reply to). For a
   channel, add the bot as an administrator instead.
2. Call the `getUpdates` endpoint and read the `chat.id` field:

   ```bash
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
   ```

   Look for `"chat":{"id":...}` in the JSON response.
3. Alternatively, message [@userinfobot](https://t.me/userinfobot), which
   replies with your numeric user (chat) ID.

## Configuration

Provide credentials through environment variables or a `.env` file.

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

`.env` (and `.venv`) are gitignored, so your secrets stay out of version
control. The recognized variables are:

- `TELEGRAM_BOT_TOKEN` - the token from @BotFather (required to send).
- `TELEGRAM_CHAT_ID` - the destination chat ID (required to send).
- `NEWS_FEED_URL` - optional. Override the default news feed URL (Hacker News
  front page). A `--feed-url` flag, if passed, takes precedence over this.

See [.env.example](.env.example) for the full template.

## Usage

Preview today's headlines without sending anything (no credentials needed):

```bash
python -m daily_tech_news --dry-run
```

Limit the number of headlines:

```bash
python -m daily_tech_news --dry-run --limit 5
```

Send to Telegram (requires the environment variables above):

```bash
python -m daily_tech_news
```

Use a different feed. Either pass `--feed-url` per run, or set the
`NEWS_FEED_URL` environment variable (the flag wins when both are set):

```bash
python -m daily_tech_news --feed-url https://example.com/rss.xml --limit 8
```

The tool exits `0` on success, `1` on a runtime error (fetch or send failure),
and `2` on a configuration error (missing credentials).

## Daily automation

### cron

Run once a day at 08:00 using cron. Edit your crontab with `crontab -e` and add a
line pointing at your virtualenv's Python (adjust the paths):

```cron
0 8 * * * cd /path/to/Daily-Tech-News && /path/to/Daily-Tech-News/.venv/bin/python -m daily_tech_news >> /path/to/Daily-Tech-News/cron.log 2>&1
```

Because cron runs with a minimal environment, either keep a `.env` file in the
project directory (it is loaded automatically) or export the variables in the
crontab entry.

### systemd timer

On systems using systemd, you can schedule delivery with a service plus a timer.

`~/.config/systemd/user/daily-tech-news.service`:

```ini
[Unit]
Description=Send daily tech news to Telegram

[Service]
Type=oneshot
WorkingDirectory=/path/to/Daily-Tech-News
ExecStart=/path/to/Daily-Tech-News/.venv/bin/python -m daily_tech_news
```

`~/.config/systemd/user/daily-tech-news.timer`:

```ini
[Unit]
Description=Run daily tech news every morning

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it with:

```bash
systemctl --user enable --now daily-tech-news.timer
```

## Testing

Install the dev dependencies (`pip install -e .[dev]`) and run:

```bash
pytest -q
```

The tests mock all HTTP (both the news fetch and the Telegram send), so they
perform no live network calls. To lint:

```bash
ruff check .
```
