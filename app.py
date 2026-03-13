from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from extract_payload import extract_payload

app = Flask(__name__)
CORS(app)

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

@app.route("/")
def home():
    return "Receiver backend running"

@app.route("/extract", methods=["POST"])
def extract():

    audio = request.files["audio"]
    key = request.form["key"]

    audio_path = os.path.join(UPLOAD, "stego.wav")
    output_img = os.path.join(UPLOAD, "recovered.png")

    audio.save(audio_path)

    mode, message = extract_payload(audio_path, key, output_img)

    # if image exists send it
    if mode & 1:
        return send_file(output_img, mimetype='image/png')

    # if text only
    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
