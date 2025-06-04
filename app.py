# app.py
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, abort, jsonify, render_template

from utils.constants import OUTPUT_PATH_SANITISED

app = Flask(__name__, static_folder="static", template_folder="templates")


def load_jobs_df() -> pd.DataFrame:
    """Read the sanitised CSV. If it doesn’t exist yet, abort with 404."""
    if not Path(OUTPUT_PATH_SANITISED).exists():
        abort(
            404,
            description="Sanitised dataset not found – run data_processing.py first.",
        )
    return pd.read_csv(OUTPUT_PATH_SANITISED)


@app.route("/")
def home():
    # get last-modified time for footer
    last_updated = (
        datetime.fromtimestamp(Path(OUTPUT_PATH_SANITISED).stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M"
        )
        if Path(OUTPUT_PATH_SANITISED).exists()
        else "N/A"
    )
    return render_template("index.html", last_updated=last_updated)


@app.route("/api/jobs")
def api_jobs():
    """
    Return the sanitised dataset as clean JSON.
    pandas → dict → replace NaN/NaT with None → jsonify
    """
    df = load_jobs_df()

    # Convert any pandas/NumPy NA values to real Python None so that Flask/jsonify
    # serialises them as valid JSON ``null`` instead of the JavaScript ``NaN``.
    cleaned = df.replace({pd.NA: None, np.nan: None}).to_dict(  # ensure NA/NaN → None
        orient="records"
    )

    return jsonify(cleaned)


if __name__ == "__main__":
    # Use `FLASK_DEBUG=1 flask run` during local dev instead
    app.run(port=8000, debug=False)
