import logging

from pathlib import Path
from utils.constants import DIRECTORY_DATA, OUTPUT_FILENAME

# ────────────────────────────────────────────────────────────────────────────────
# SET UP BASIC LOGGING
# ────────────────────────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

# ────────────────────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────────────────────
def get_csv_path(root_dir: Path = None) -> Path:
    """
    Create '<project_root>/data/' if it does not exist, and return the Path.
    """
    if root_dir is None:
        root_dir = Path(__file__).resolve().parent.parent

    data_dir = root_dir / DIRECTORY_DATA

    if not data_dir.exists():
        logging.debug(f"Creating data directory at: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
    else:
        logging.debug(f"Data directory already exists: {data_dir}")

    csv_path = data_dir / OUTPUT_FILENAME
    logging.debug(f"CSV path: {csv_path}")

    return csv_path
