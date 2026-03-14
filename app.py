from flask import Flask, request, jsonify, send_file
import os
import cv2
from extract_audio import extract_payload

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)


@app.route("/")
def home():
    return "Receiver Backend Running"


@app.route("/extract", methods=["POST"])
def extract():
    try:

        # check if audio exists
        if "audio" not in request.files:
            return jsonify({"error": "Audio file not provided"})

        audio = request.files["audio"]

        # check if key exists
        key = request.form.get("key")
        if not key:
            return jsonify({"error": "Secret key not provided"})

        # save uploaded audio
        audio_path = os.path.join(UPLOAD, "input.wav")
        audio.save(audio_path)

        # run extraction algorithm
        image, text = extract_payload(audio_path, key)

        result = {}

        # handle extracted image
        if image is not None:
            img_path = os.path.join(UPLOAD, "extracted.png")
            cv2.imwrite(img_path, image)
            result["image_available"] = True
        else:
            result["image_available"] = False

        # handle extracted text
        if text:
            result["text"] = text
        else:
            result["text"] = ""

        return jsonify(result)

    except Exception as e:
        # return actual error message
        return jsonify({"error": str(e)})


@app.route("/download_image")
def download_image():

    img_path = os.path.join(UPLOAD, "extracted.png")

    if os.path.exists(img_path):
        return send_file(img_path, as_attachment=True)

    return jsonify({"error": "No image found"})


if __name__ == "__main__":
    app.run(debug=True)
