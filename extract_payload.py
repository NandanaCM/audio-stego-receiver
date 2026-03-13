import numpy as np
import wave
import hashlib
import cv2

def extract_payload(audio_path, key, output_image):

    wav = wave.open(audio_path, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    audio_samples = np.frombuffer(frames, dtype=np.int16)

    def hash_func(msb, key):
        return int(hashlib.sha256((str(msb) + key).encode()).hexdigest(), 16)

    payload_bits = []

    for sample in audio_samples:

        msb = (sample >> 8) & 0xFF

        if hash_func(msb, key) % 10 == 0:

            b1 = (sample >> 1) & 1
            b3 = (sample >> 3) & 1

            payload_bits.append(b1)
            payload_bits.append(b3)

            # Stop after header first
            if len(payload_bits) >= 72:
                break

    payload_bits = np.array(payload_bits, dtype=np.uint8)

    header_bits = payload_bits[:72]

    mode = int("".join(map(str, header_bits[0:8])), 2)
    img_len = int("".join(map(str, header_bits[8:40])), 2)
    text_len = int("".join(map(str, header_bits[40:72])), 2)

    required_bits = 72 + img_len + text_len

    payload_bits = []

    for sample in audio_samples:

        msb = (sample >> 8) & 0xFF

        if hash_func(msb, key) % 10 == 0:

            b1 = (sample >> 1) & 1
            b3 = (sample >> 3) & 1

            payload_bits.append(b1)
            payload_bits.append(b3)

            if len(payload_bits) >= required_bits:
                break

    payload_bits = np.array(payload_bits, dtype=np.uint8)

    payload = payload_bits[72:72 + img_len + text_len]

    if mode & 1:

        img_bits = payload[:img_len]

        img_bytes = np.packbits(img_bits)

        image = img_bytes.reshape((64, 64))

        cv2.imwrite(output_image, image)

    message = ""

    if mode & 2:

        text_bits = payload[img_len:img_len + text_len]

        chars = []

        for i in range(0, len(text_bits), 8):
            byte = text_bits[i:i+8]
            byte = int("".join(map(str, byte)), 2)
            chars.append(chr(byte))

        message = "".join(chars)

    return mode, message
