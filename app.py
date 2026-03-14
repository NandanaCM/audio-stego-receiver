from flask import Flask, request, jsonify, send_file
import os
import cv2
from extract_audio import extract_payload

app = Flask(__name__)

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)


@app.route("/")
def home():
    return "Receiver Backend Running"


@app.route("/extract", methods=["POST"])
def extract():

    audio = request.files["audio"]
    key = request.form["key"]

    audio_path = os.path.join(UPLOAD, "input.wav")
    audio.save(audio_path)

    image, text = extract_payload(audio_path, key)

    result = {}

    # Save image if exists
    if image is not None:

        img_path = os.path.join(UPLOAD, "extracted.png")
        cv2.imwrite(img_path, image)

        result["image_available"] = True

    else:
        result["image_available"] = False

    # Send text if exists
    if text is not None:
        result["text"] = text
    else:
        result["text"] = ""

    return jsonify(result)


@app.route("/download_image")
def download_image():

    img_path = os.path.join(UPLOAD, "extracted.png")

    if os.path.exists(img_path):
        return send_file(img_path, as_attachment=True)

    return "No image found"


if __name__ == "__main__":
    app.run(debug=True)
