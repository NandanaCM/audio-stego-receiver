import numpy as np
import wave
import hashlib
import cv2

def bits_to_text(bits):
    chars = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        chars.append(chr(int(byte,2)))
    return ''.join(chars)


def bits_to_bytes(bits):
    byte_array = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        byte_array.append(int(byte,2))
    return bytes(byte_array)


def extract_payload(stego_audio, key):

    # read audio
    wav = wave.open(stego_audio, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    samples = np.frombuffer(frames, dtype=np.int16)

    # extract LSB
    bits = [str(sample & 1) for sample in samples]
    bitstream = ''.join(bits)

    pointer = 0

    # ---------------------------
    # Extract TEXT
    # ---------------------------

    text_len_bits = bitstream[pointer:pointer+32]
    text_len = int(text_len_bits,2)
    pointer += 32

    if text_len > 0:

        text_bits = bitstream[pointer:pointer+text_len]
        pointer += text_len

        text = bits_to_text(text_bits)

        print("Hidden Text Found:")
        print(text)

    else:
        print("No hidden text found")


    # ---------------------------
    # Extract IMAGE
    # ---------------------------

    img_len_bits = bitstream[pointer:pointer+32]
    img_len = int(img_len_bits,2)
    pointer += 32

    if img_len > 0:

        img_bits = bitstream[pointer:pointer+img_len]

        img_bytes = bits_to_bytes(img_bits)

        with open("recovered_image.png","wb") as f:
            f.write(img_bytes)

        print("Hidden image recovered as recovered_image.png")

    else:
        print("No hidden image found")


# run
stego_audio = input("Enter Stego Audio File: ")
key = input("Enter Secret Key: ")

extract_payload(stego_audio, key)
