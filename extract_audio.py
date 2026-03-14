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

    chunk_size = 4096

    def hash_func(msb, key):
        return int(hashlib.sha256((str(msb) + key).encode()).hexdigest(), 16)

    header_bits = []
    payload_bits = []

    mode = None
    img_len = None
    text_len = None
    payload_required = None

    while True:

        frames = wav.readframes(chunk_size)
        if not frames:
            break

        samples = np.frombuffer(frames, dtype=np.int16)

        # convert stereo to mono
        if wav.getnchannels() == 2:
            samples = samples.reshape(-1, 2)
            samples = samples.mean(axis=1).astype(np.int16)

        for sample in samples:

            msb = (sample >> 8) & 0xFF

            if hash_func(msb, key) % 10 == 0:

                bit1 = (sample >> 1) & 1
                bit3 = (sample >> 3) & 1

                for bit in [bit1, bit3]:

                    # extract header first
                    if mode is None:
                        header_bits.append(bit)

                        if len(header_bits) == 72:
                            mode = int("".join(map(str, header_bits[0:8])), 2)
                            img_len = int("".join(map(str, header_bits[8:40])), 2)
                            text_len = int("".join(map(str, header_bits[40:72])), 2)

                            payload_required = img_len + text_len

                    else:

                        if len(payload_bits) < payload_required:
                            payload_bits.append(bit)

                        if len(payload_bits) >= payload_required:
                            wav.close()
                            break

            if payload_required and len(payload_bits) >= payload_required:
                break

        if payload_required and len(payload_bits) >= payload_required:
            break

    wav.close()

    index = 0
    image = None
    text = None

    if mode & 1:

        img_bits = payload_bits[index:index + img_len]
        index += img_len

        img_bytes = np.packbits(img_bits)

        if len(img_bytes) >= 4096:
            image = img_bytes[:4096].reshape((64, 64))

    if mode & 2:

        text_bits = payload_bits[index:index + text_len]
        text = bits_to_text(text_bits)

    return image, text
