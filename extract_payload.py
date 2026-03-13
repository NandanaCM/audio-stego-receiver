import wave
import hashlib


def hash_func(msb, key):
    return int(hashlib.sha256((str(msb) + key).encode()).hexdigest(), 16)


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


def extract_payload(audio_file, key, output_img):

    wav = wave.open(audio_file, 'rb')

    bits = []
    HEADER_SIZE = 72
    payload_size = None

    index = 0

    while True:

        frame = wav.readframes(1)
        if not frame:
            break

        sample = int.from_bytes(frame[:2], byteorder='little', signed=True)

        # skip samples to speed up extraction
        if index % 10 != 0:
            index += 1
            continue

        msb = (sample >> 8) & 0xFF

        if hash_func(msb, key) % 10 == 0:

            bits.append(str((sample >> 1) & 1))
            bits.append(str((sample >> 3) & 1))

            if len(bits) == HEADER_SIZE:

                header = ''.join(bits)

                mode = int(header[0:8], 2)
                img_len = int(header[8:40], 2)
                text_len = int(header[40:72], 2)

                payload_size = HEADER_SIZE + img_len + text_len

            if payload_size and len(bits) >= payload_size:
                break

        index += 1

    wav.close()

    bits = ''.join(bits)

    if len(bits) < HEADER_SIZE:
        return 0, ""

    pointer = 0

    mode = int(bits[pointer:pointer+8], 2)
    pointer += 8

    img_len = int(bits[pointer:pointer+32], 2)
    pointer += 32

    text_len = int(bits[pointer:pointer+32], 2)
    pointer += 32

    message = ""
    image_found = False

    if img_len > 0:

        img_bits = bits[pointer:pointer+img_len]
        pointer += img_len

        img_bytes = bits_to_bytes(img_bits)

        with open(output_img, "wb") as f:
            f.write(img_bytes)

        image_found = True

    if text_len > 0:

        text_bits = bits[pointer:pointer+text_len]
        message = bits_to_text(text_bits)

    if image_found and message:
        return 3, message

    if image_found:
        return 1, ""

    if message:
        return 2, message

    return 0, ""
