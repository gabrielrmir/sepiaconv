import sys
import threading
from PIL import Image
import numpy as np

def usage():
    print('Usage: sepiaconv.py <file>')

def load_image(filename):
    try:
        im = Image.open(filename)
    except:
        print('[ERROR] Could not load image.')
        exit(1)

    return im

def pixel_to_sepia(rgb):
    r,g,b    = rgb
    newRed   = min(int(0.393*r + 0.769*g + 0.189*b),255)
    newGreen = min(int(0.349*r + 0.686*g + 0.168*b),255)
    newBlue  = min(int(0.272*r + 0.534*g + 0.131*b),255)
    return [newRed, newGreen, newBlue]

# Divide image into chunks of smaller size
def chunkify(im, subdivs):
    cells = (subdivs+1)**2
    width = im.width//(subdivs+1)
    height = im.height//(subdivs+1)
    chunks = []

    for i in range(cells):
        left = (i%(subdivs+1))*width
        top = (i//(subdivs+1))*height
        right = left+width
        bottom = top+height
        chunks.append(im.crop((left,top,right,bottom)))

    return chunks

def image_to_sepia(im):
    im = np.asarray(im,copy=True)
    h = len(im)
    w = len(im[0])

    for row in range(h):
        for col in range(w):
            sep = pixel_to_sepia(im[row][col])
            im[row][col] = sep

    im = Image.fromarray(im, 'RGB')
    return im

def chunk_processor(target_im):
    while True:
        with lock:
            if len(data) == 0: break
            chunk, pos = data.pop()

        sepia = image_to_sepia(chunk)

        with lock:
            target_im.paste(sepia, pos)

def main():
    argv = sys.argv
    argc = len(argv)

    if argc != 2:
        usage()
        exit(1)

    im = load_image(argv[1])

    subdivs = 3
    rows = subdivs+1
    chunks = chunkify(im, subdivs)

    newim = Image.new("RGB", im.size)

    threads = []
    for i in range(1):
        t = threading.Thread(target=chunk_processor, args=(newim,))
        threads.append(t)

    x,y = (0,0)
    for i in range(len(chunks)):
        chunk = chunks[i]
        data.append((chunk.copy(), (x,y)))

        x += chunk.width
        if (i+1)%rows == 0:
            x = 0
            y += chunk.height

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    newim.save("out.jpg")

lock = threading.Lock()
data = []

if __name__ == '__main__':
    main()
