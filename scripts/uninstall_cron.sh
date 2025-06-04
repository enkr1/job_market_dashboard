#!/bin/bash

# Define the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define the path to the Python executable within the virtual environment
PYTHON_EXEC="$PROJECT_DIR/.venv/bin/python"

# Define the cron job entry to remove
CRON_JOB="*/5 * * * * cd \"$PROJECT_DIR\" && \"$PYTHON_EXEC\" -m scraper.selenium_scraper >> \"$PROJECT_DIR/logs/cron.log\" 2>&1"

# Remove the cron job entry
crontab -l 2>/dev/null | grep -vF "$CRON_JOB" | crontab -
