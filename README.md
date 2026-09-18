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

The tool is designed to run once a day. The examples below schedule it for
**9:00am Malaysia time (Asia/Kuala_Lumpur, UTC+8)**.

> cron runs with a minimal environment, so it will not pick up variables from
> your shell. Keep a `.env` file with `TELEGRAM_BOT_TOKEN` and
> `TELEGRAM_CHAT_ID` in the project directory (it is loaded automatically), or
> export the variables in the crontab entry. Copy the template first:
> `cp .env.example .env`.

### cron (install script)

The quickest way is the bundled install script. It resolves the project and
virtualenv paths from its own location, installs a crontab entry for the current
user pinned to Malaysia time, appends output to `cron.log`, and is idempotent
(re-running it will not add a duplicate entry):

```bash
./scripts/install-cron.sh
```

It requires the `crontab` command to be available and prints a clear error and
exits non-zero if it is not. It also warns (but still installs) if the
virtualenv or `.env` file is missing.

### cron (manual)

If you prefer to edit the crontab yourself, run `crontab -e` and add the
following. The `CRON_TZ` line pins the schedule to Malaysia time on Linux/Vixie
cron, so `0 9 * * *` fires at 09:00 local Malaysia time regardless of the system
timezone (adjust the paths):

```cron
# daily-tech-news
CRON_TZ=Asia/Kuala_Lumpur
0 9 * * * cd /path/to/Daily-Tech-News && /path/to/Daily-Tech-News/.venv/bin/python -m daily_tech_news >> /path/to/Daily-Tech-News/cron.log 2>&1
```

If your cron implementation does not support `CRON_TZ`, omit that line and use
the plain-UTC equivalent instead (09:00 Malaysia time is 01:00 UTC):

```cron
# daily-tech-news
0 1 * * * cd /path/to/Daily-Tech-News && /path/to/Daily-Tech-News/.venv/bin/python -m daily_tech_news >> /path/to/Daily-Tech-News/cron.log 2>&1
```

### Verify and remove

```bash
crontab -l   # list current entries (look for the "# daily-tech-news" marker)
crontab -e   # edit entries; delete the marked block to remove the job
```

### GitHub Actions (runs in the cloud, no machine of your own)

If you would rather not keep a machine running, a bundled GitHub Actions
workflow ([.github/workflows/daily-tech-news.yml](.github/workflows/daily-tech-news.yml))
runs the tool unattended on GitHub's infrastructure and sends the daily news to
your Telegram.

1. Push this repository to GitHub (or use your fork).
2. Add your credentials as repository secrets: go to **Settings → Secrets and
   variables → Actions → New repository secret** and create two secrets:
   - `TELEGRAM_BOT_TOKEN` - the token from @BotFather.
   - `TELEGRAM_CHAT_ID` - the destination chat ID.

   The workflow reads these secrets and injects them into the run step's
   environment; nothing is hardcoded in the repository.
3. The workflow is scheduled with a `cron` trigger. GitHub Actions cron is
   **always in UTC** and has no timezone support, so the schedule is
   `0 1 * * *` (**01:00 UTC = 09:00 Malaysia time**, Asia/Kuala_Lumpur, UTC+8).
4. To test it right away, trigger a manual run: open the **Actions** tab, select
   the **Daily Tech News** workflow, and click **Run workflow** (this uses the
   workflow's `workflow_dispatch` trigger).

> Note: GitHub may delay or skip scheduled runs when the service is under heavy
> load, and schedules on free plans are paused after a period of repository
> inactivity. Use the manual **Run workflow** button any time you want an
> on-demand delivery.

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
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it with:

```bash
systemctl --user enable --now daily-tech-news.timer
```

`OnCalendar` uses the system timezone. If your machine is not set to Malaysia
time, either pin the timezone by adding `Environment=TZ=Asia/Kuala_Lumpur` under
`[Service]` and setting `OnCalendar=*-*-* 09:00:00`, or use the UTC equivalent
`OnCalendar=*-*-* 01:00:00`.

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
