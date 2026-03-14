import numpy as np
import cv2
import wave
import hashlib


def bits_to_text(bits):

    chars = []

    for i in range(0, len(bits), 8):

        byte = bits[i:i+8]

        if len(byte) < 8:
            break

        chars.append(chr(int("".join(map(str, byte)), 2)))

    return "".join(chars)


def extract_payload(audio_path, key):

    wav = wave.open(audio_path, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    audio_samples = np.frombuffer(frames, dtype=np.int16)

    extracted_bits = []

    def hash_func(msb, key):
        return int(hashlib.sha256((str(msb) + key).encode()).hexdigest(), 16)

    # extract bits
    for sample in audio_samples:

        msb = (sample >> 8) & 0xFF

        if hash_func(msb, key) % 10 == 0:

            bit1 = (sample >> 1) & 1
            bit3 = (sample >> 3) & 1

            extracted_bits.append(bit1)
            extracted_bits.append(bit3)

    extracted_bits = np.array(extracted_bits)

    # HEADER
    mode = int("".join(map(str, extracted_bits[0:8])), 2)
    img_len = int("".join(map(str, extracted_bits[8:40])), 2)
    text_len = int("".join(map(str, extracted_bits[40:72])), 2)

    index = 72

    image = None
    text = None

    # IMAGE
    if mode & 1:

        img_bits = extracted_bits[index:index + img_len]
        index += img_len

        img_bytes = np.packbits(img_bits)

        image = img_bytes.reshape((64, 64))

    # TEXT
    if mode & 2:

        text_bits = extracted_bits[index:index + text_len]
        text = bits_to_text(text_bits)

    return image, text
