import numpy as np
import wave
import hashlib


def bits_to_text(bits):
    chars=[]
    for i in range(0,len(bits),8):
        byte=bits[i:i+8]
        if len(byte)==8:
            chars.append(chr(int(byte,2)))
    return ''.join(chars)


def bits_to_bytes(bits):
    data=[]
    for i in range(0,len(bits),8):
        byte=bits[i:i+8]
        if len(byte)==8:
            data.append(int(byte,2))
    return bytes(data)


def extract_payload(audio_file,key,output_img):

    wav=wave.open(audio_file,'rb')
    frames=wav.readframes(wav.getnframes())
    wav.close()

    samples=np.frombuffer(frames,dtype=np.int16)

    bits=[]

    def hash_func(msb,key):
        return int(hashlib.sha256((str(msb)+key).encode()).hexdigest(),16)

    # SPEED FIX: process every 50th sample
    for i in range(0,len(samples),50):

        sample=samples[i]
        msb=(sample>>8)&0xFF

        if hash_func(msb,key)%10==0:

            bit1=(sample>>1)&1
            bit2=(sample>>3)&1

            bits.append(str(bit1))
            bits.append(str(bit2))

    bits=''.join(bits)

    pointer=0

    if len(bits)<72:
        return 0,"No hidden data"

    mode=int(bits[pointer:pointer+8],2)
    pointer+=8

    img_len=int(bits[pointer:pointer+32],2)
    pointer+=32

    text_len=int(bits[pointer:pointer+32],2)
    pointer+=32

    message=""
    image_found=False

    if img_len>0 and pointer+img_len<=len(bits):

        img_bits=bits[pointer:pointer+img_len]
        pointer+=img_len

        img_bytes=bits_to_bytes(img_bits)

        with open(output_img,"wb") as f:
            f.write(img_bytes)

        image_found=True

    if text_len>0 and pointer+text_len<=len(bits):

        text_bits=bits[pointer:pointer+text_len]
        message=bits_to_text(text_bits)

    if image_found and message:
        return 3,message

    if image_found:
        return 1,""

    if message:
        return 2,message

    return 0,"No hidden data"
