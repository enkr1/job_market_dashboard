#!/bin/bash
set -e

echo "-------------------------------------------"
echo "🚀 Automated Setup for Job Market Dashboard"
echo "-------------------------------------------"

# 1. Check Python 3 installation
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required but not installed. Aborting."
    exit 1
fi

PY_VER=$(python3 --version | awk '{print $2}')
echo "✔️  Python 3 detected (version: $PY_VER)"

# 2. Create & activate virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "🛡️  Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "🟢 Virtual environment '.venv' activated."

# 3. Upgrade pip inside venv
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# 4. Install main dependencies
echo ""
echo "📦 Installing main dependencies..."
pip install -r requirements.txt

# 5. Install dev dependencies (optional)
if [ -f requirements-dev.txt ]; then
    echo "🧪 Installing dev dependencies (optional)..."
    pip install -r requirements-dev.txt || echo "⚠️  (Dev dependencies optional, continuing even if failed.)"
else
    echo "ℹ️  No requirements-dev.txt found, skipping dev dependencies."
fi

# 6. Run tests (safe to fail)
echo ""
echo "🧪 Running tests (pytest)..."
python -m pytest || echo "⚠️  (Some tests failed or pytest not found; continuing...)"

# 7. Run scraper as smoke test
echo ""
echo "🕵️  Running scraper once for smoke test..."
python -m scraper.selenium_scraper || {
    echo "❌ Scraper failed to run. Please check your setup."
    deactivate
    exit 1
}

# 8. Cron job install
echo ""
echo "⏰ Setting up scheduled scraping via cron job..."
chmod +x scripts/*
./scripts/install_cron.sh

# 9. Show output file locations
echo ""
echo "📁 Scraped data and generated charts will be saved to:"
echo "   - data/techinasia_jobs_*.csv"
echo "   - data/charts/*.png"

# 10. Show crontab and uninstall reminder
echo ""
echo "⏱️  Cron job installed! (Check with: crontab -l)"
echo "   To remove the cron job later, run:"
echo "      ./scripts/uninstall_cron.sh"
echo ""
echo "✅ Setup complete. Happy hacking!"

# 11. Ask if user wants to start the server
read -p "👉 Start the server now (python app.py)? [y/N]: " start_srv
if [[ "$start_srv" =~ ^[Yy]$ ]]; then
    echo "🌐 Starting server..."
    python app.py
else
    echo "ℹ️  Skipping server start. You can run: source .venv/bin/activate && python app.py"
fi

# 12. Deactivate venv on script exit
deactivate
