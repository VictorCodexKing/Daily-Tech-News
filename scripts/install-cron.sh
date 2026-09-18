#!/usr/bin/env bash
#
# install-cron.sh - install a crontab entry that runs Daily Tech News every day
# at 9:00am Malaysia time (Asia/Kuala_Lumpur, UTC+8).
#
# The entry is installed for the current user. Credentials are NOT baked into
# the crontab; the tool reads TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID from a .env
# file in the project directory at runtime (cron runs with a minimal
# environment), so make sure that .env exists before relying on the schedule.
#
# Re-running this script is safe: it detects an existing entry via a marker
# comment and does nothing instead of adding a duplicate.
set -euo pipefail

# A unique marker so we can find (or remove) our own entry later.
MARKER="# daily-tech-news"

# Resolve the project directory relative to this script's location, so the
# script works regardless of the current working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
LOG_FILE="${PROJECT_DIR}/cron.log"

# Pin the timezone unambiguously. On Linux/Vixie cron, CRON_TZ makes the
# schedule below fire at 09:00 Malaysia time regardless of the system timezone.
CRON_TZ_LINE="CRON_TZ=Asia/Kuala_Lumpur"
SCHEDULE="0 9 * * *"

if ! command -v crontab >/dev/null 2>&1; then
    echo "Error: 'crontab' is not available on this system." >&2
    echo "Install a cron implementation (e.g. cronie or vixie-cron), or use the" >&2
    echo "systemd timer described in the README instead." >&2
    exit 1
fi

if [ ! -x "${VENV_PYTHON}" ]; then
    echo "Warning: no virtualenv Python found at ${VENV_PYTHON}." >&2
    echo "Create it first, e.g.:" >&2
    echo "  python3.12 -m venv ${PROJECT_DIR}/.venv" >&2
    echo "  ${PROJECT_DIR}/.venv/bin/pip install -e ${PROJECT_DIR}" >&2
    echo "Continuing to install the crontab entry anyway; it will start working" >&2
    echo "once the virtualenv exists." >&2
fi

if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo "Warning: no .env file found at ${PROJECT_DIR}/.env." >&2
    echo "cron runs with a minimal environment, so create it with your" >&2
    echo "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID before the schedule can send." >&2
    echo "  cp ${PROJECT_DIR}/.env.example ${PROJECT_DIR}/.env" >&2
fi

# The command cron will run: change into the project dir (so .env is picked up)
# and run the tool via the venv Python, appending all output to the log file.
CRON_COMMAND="cd ${PROJECT_DIR} && ${VENV_PYTHON} -m daily_tech_news >> ${LOG_FILE} 2>&1"

# Read the existing crontab (empty if none is installed yet).
EXISTING_CRONTAB="$(crontab -l 2>/dev/null || true)"

if printf '%s\n' "${EXISTING_CRONTAB}" | grep -qF "${MARKER}"; then
    echo "A Daily Tech News cron entry is already installed; nothing to do."
    echo "Current entry:"
    printf '%s\n' "${EXISTING_CRONTAB}" | grep -A2 -F "${MARKER}"
    echo
    echo "To view or edit it:   crontab -l   /   crontab -e"
    exit 0
fi

# Append our block (marker + timezone + schedule) to the existing crontab.
{
    printf '%s\n' "${EXISTING_CRONTAB}"
    printf '%s\n' "${MARKER}"
    printf '%s\n' "${CRON_TZ_LINE}"
    printf '%s %s\n' "${SCHEDULE}" "${CRON_COMMAND}"
} | crontab -

echo "Installed a cron entry to run Daily Tech News daily at 09:00 Asia/Kuala_Lumpur."
echo "  Project:  ${PROJECT_DIR}"
echo "  Python:   ${VENV_PYTHON}"
echo "  Log file: ${LOG_FILE}"
echo
echo "Verify with:  crontab -l"
echo "Edit with:    crontab -e"
echo "Remove with:  crontab -l | grep -v '${MARKER}' | crontab -   (also drop the CRON_TZ/schedule lines)"
