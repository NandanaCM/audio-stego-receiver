import numpy as np
import wave
import hashlib


def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def bits_to_bytes(bits):
    data = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            data.append(int(byte, 2))
    return bytes(data)


def hash_func(msb, key):
    return int(hashlib.sha256((str(msb) + key).encode()).hexdigest(), 16)


def extract_payload(audio_file, key, output_img):

    wav = wave.open(audio_file, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    samples = np.frombuffer(frames, dtype=np.int16)

    header_bits = []
    payload_bits = []

    header_size = 72  # 8 + 32 + 32
    pointer = 0

    img_len = 0
    text_len = 0
    payload_needed = None

    for sample in samples:

        msb = (sample >> 8) & 0xFF

        if hash_func(msb, key) % 10 == 0:

            bit1 = (sample >> 1) & 1
            bit2 = (sample >> 3) & 1

            for b in [bit1, bit2]:

                # collect header first
                if len(header_bits) < header_size:
                    header_bits.append(str(b))

                    if len(header_bits) == header_size:

                        bits = ''.join(header_bits)

                        mode = int(bits[0:8], 2)
                        img_len = int(bits[8:40], 2)
                        text_len = int(bits[40:72], 2)

                        payload_needed = img_len + text_len

                else:

                    payload_bits.append(str(b))

                    if len(payload_bits) >= payload_needed:
                        break

        if payload_needed and len(payload_bits) >= payload_needed:
            break

    message = ""
    image_found = False

    pointer = 0

    if img_len > 0:

        img_bits = payload_bits[pointer:pointer+img_len]
        pointer += img_len

        img_bytes = bits_to_bytes(img_bits)

        with open(output_img, "wb") as f:
            f.write(img_bytes)

        image_found = True

    if text_len > 0:

        text_bits = payload_bits[pointer:pointer+text_len]
        message = bits_to_text(text_bits)

    if image_found and message:
        return 3, message

    if image_found:
        return 1, ""

    if message:
        return 2, message

    return 0, ""
