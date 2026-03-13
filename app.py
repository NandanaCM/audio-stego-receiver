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

    try:

        audio = request.files["audio"]
        key = request.form["key"]

        audio_path = os.path.join(UPLOAD, "stego.wav")
        output_img = os.path.join(UPLOAD, "recovered.png")

        audio.save(audio_path)

        mode, message = extract_payload(audio_path, key, output_img)

        if mode == 3:
            return jsonify({
                "text": message,
                "image": True
            })

        if mode == 1:
            return send_file(output_img, mimetype="image/png")

        if mode == 2:
            return jsonify({"text": message})

        return jsonify({"text": "No hidden data found"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)

