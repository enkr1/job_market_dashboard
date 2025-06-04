#!/bin/bash

# Define the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define the path to the Python executable within the virtual environment
PYTHON_EXEC="$PROJECT_DIR/.venv/bin/python"

# Define the log file path
LOG_FILE="$PROJECT_DIR/logs/cron.log"

# Ensure the logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Create the cron job entry
CRON_JOB="*/5 * * * * cd \"$PROJECT_DIR\" && \"$PYTHON_EXEC\" -m scraper.selenium_scraper >> \"$LOG_FILE\" 2>&1"

# Install the cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
