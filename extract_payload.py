import numpy as np
import wave
import hashlib


def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        chars.append(chr(int(bits[i:i+8], 2)))
    return ''.join(chars)


def bits_to_bytes(bits):
    data = []
    for i in range(0, len(bits), 8):
        data.append(int(bits[i:i+8], 2))
    return bytes(data)


def extract_payload(audio_file, key, output_img):

    wav = wave.open(audio_file, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    samples = np.frombuffer(frames, dtype=np.int16)

    bits = ''.join([str(sample & 1) for sample in samples])

    pointer = 0

    # HASH
    hash_len = int(bits[pointer:pointer+32], 2)
    pointer += 32

    hash_bits = bits[pointer:pointer+hash_len]
    pointer += hash_len

    received_hash = bits_to_text(hash_bits)

    # TEXT
    text_len = int(bits[pointer:pointer+32], 2)
    pointer += 32

    message = ""

    if text_len > 0:

        text_bits = bits[pointer:pointer+text_len]
        pointer += text_len

        hidden_text = bits_to_text(text_bits)

        verify_hash = hashlib.sha256(
            (hidden_text + key).encode()
        ).hexdigest()

        if verify_hash == received_hash:
            message = hidden_text
        else:
            message = "Hash verification failed"

    # IMAGE
    img_len = int(bits[pointer:pointer+32], 2)
    pointer += 32

    mode = 0

    if img_len > 0:

        img_bits = bits[pointer:pointer+img_len]
        img_bytes = bits_to_bytes(img_bits)

        with open(output_img, "wb") as f:
            f.write(img_bytes)

        mode = 1

    return mode, message
