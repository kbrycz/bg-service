import logging
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

from bg_removal import remove_bg_from_bytes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB max

# Only allow these specific origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://www.nocabot.com",
            "https://removebg.nocabot.com"
        ]
    }
})

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def health_check():
    return "Background Removal Flask service (lighter model + downscale) is running!", 200

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    """
    Accept up to 5 images in 'images' form field, remove their backgrounds,
    and return an array of base64-encoded PNGs in JSON.
    Downscale images first and use a lighter rembg model to reduce memory usage.
    """
    try:
        if "images" not in request.files:
            logging.warning("No 'images' field in request.")
            return jsonify({"error": "No images provided"}), 400

        files = request.files.getlist("images")
        if not files or len(files) == 0:
            logging.warning("Empty file list in 'images'.")
            return jsonify({"error": "No images provided"}), 400

        results = []
        for f in files:
            filename = secure_filename(f.filename) or "untitled"
            try:
                image_bytes = f.read()
                removed_b64 = remove_bg_from_bytes(image_bytes)
                results.append({"removed_b64": removed_b64})
                logging.info(f"Background removed successfully for file {filename}")
            except Exception as e:
                logging.error(f"Error removing background for file {filename}", exc_info=True)
                # Return null for that file
                results.append({"removed_b64": None})

        return jsonify({"images": results}), 200

    except Exception as e:
        logging.error("General error in /remove-bg endpoint", exc_info=True)
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)