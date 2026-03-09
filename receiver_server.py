from flask import Flask, request, send_file
from flask_cors import CORS
import os
from extract_audio import extract_image

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
    output_img = os.path.join(UPLOAD, "output.png")

    audio.save(audio_path)

    extract_image(audio_path, key, output_img)

    return send_file(output_img, mimetype="image/png")

if __name__ == "__main__":
    app.run()