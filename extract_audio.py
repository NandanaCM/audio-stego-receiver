import numpy as np
import wave
import hashlib
import cv2

def extract_image(audio_path, key, output_image):

    wav = wave.open(audio_path, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()

    audio_samples = np.frombuffer(frames, dtype=np.int16)

    def hash_func(index, key):
        return int(hashlib.sha256((str(index)+key).encode()).hexdigest(),16)

    bits = []

    for i, sample in enumerate(audio_samples):

        if hash_func(i, key) % 10 == 0:

            b1 = (sample >> 1) & 1
            b3 = (sample >> 3) & 1

            bits.append(b1)
            bits.append(b3)

            if len(bits) >= 64*64*8:
                break

    bits = np.array(bits[:64*64*8], dtype=np.uint8)

    img = np.packbits(bits).reshape((64,64))

    cv2.imwrite(output_image, img)