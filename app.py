

from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GALLERY_DIR = STATIC_DIR / "gallery"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/save-image")
def save_image():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image")

    if not image_data or not isinstance(image_data, str):
        return jsonify({"success": False, "error": "No image data provided."}), 400

    prefix = "data:image/png;base64,"
    if not image_data.startswith(prefix):
        return jsonify({"success": False, "error": "Expected a PNG data URL."}), 400

    try:
        encoded = image_data[len(prefix):]
        image_bytes = base64.b64decode(encoded)
    except Exception:
        return jsonify({"success": False, "error": "Could not decode image data."}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"drawing_{timestamp}.png"
    filepath = GALLERY_DIR / filename

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return jsonify({
        "success": True,
        "filename": filename,
        "url": f"/gallery/{filename}",
    })


@app.get("/gallery-images")
def gallery_images():
    files = sorted(
        [f.name for f in GALLERY_DIR.glob("*.png")],
        reverse=True,
    )
    return jsonify({
        "images": [f"/gallery/{name}" for name in files]
    })


@app.get("/gallery/<path:filename>")
def gallery_file(filename: str):
    return send_from_directory(GALLERY_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
