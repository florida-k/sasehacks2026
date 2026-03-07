from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GALLERY_DIR = STATIC_DIR / "gallery"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/save-image")
def save_image():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image")

    if not image_data:
        return jsonify({"success": False})

    prefix = "data:image/png;base64,"
    image_data = image_data.replace(prefix, "")

    image_bytes = base64.b64decode(image_data)

    filename = f"drawing_{datetime.now().timestamp()}.png"
    filepath = GALLERY_DIR / filename

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return jsonify({
        "success": True,
        "url": f"/gallery/{filename}"
    })


@app.get("/gallery-images")
def gallery_images():
    files = sorted(GALLERY_DIR.glob("*.png"), reverse=True)

    return jsonify({
        "images": [f"/gallery/{f.name}" for f in files]
    })


@app.get("/gallery/<path:filename>")
def gallery_file(filename: str):
    return send_from_directory(GALLERY_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)