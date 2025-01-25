import logging
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS


# Or to be more specific, e.g. only from localhost:3000:
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})
from bg_removal import remove_bg_from_bytes

app = Flask(__name__)

# For dev, you can allow all origins:
CORS(app)

# Optional: If you want to configure logging level
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def health_check():
    return "Background Removal Flask service is running!", 200


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    """
    Accept up to 5 images in 'images' form field, remove their backgrounds,
    and return an array of base64-encoded PNGs in JSON.
    """
    try:
        # Check if 'images' is in the request
        if "images" not in request.files:
            logging.warning("No 'images' field in request.")
            return jsonify({"error": "No images provided"}), 400

        files = request.files.getlist("images")
        if not files or len(files) == 0:
            logging.warning("Empty file list in 'images'.")
            return jsonify({"error": "No images provided"}), 400

        # Process each image
        results = []
        for f in files:
            filename = secure_filename(f.filename) or "untitled"
            try:
                image_bytes = f.read()
                # Remove background
                removed_b64 = remove_bg_from_bytes(image_bytes)
                # We'll store each result in an array
                results.append({"removed_b64": removed_b64})
                logging.info(f"Background removed successfully for file {filename}")
            except Exception as e:
                logging.error(f"Error removing background for file {filename}", exc_info=True)
                # Append null if it fails for this file
                results.append({"removed_b64": None})

        # Return JSON with an array of results
        return jsonify({"images": results}), 200

    except Exception as e:
        logging.error("General error in /remove-bg endpoint", exc_info=True)
        return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    # By default, Flask listens on port 5000. Adjust if you want a different port.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)