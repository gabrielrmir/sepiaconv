import sys
from PIL import Image
import numpy as np

def usage():
    print('Usage: sepiaconv.py <file>')

def loadimage(filename):
    try:
        im = Image.open(filename)
    except:
        print('[ERROR] Could not load image.')
        exit(1)

    return np.asarray(im,copy=True)

def pixeltosepia(rgb):
    r,g,b    = rgb
    newRed   = min(int(0.393*r + 0.769*g + 0.189*b),255)
    newGreen = min(int(0.349*r + 0.686*g + 0.168*b),255)
    newBlue  = min(int(0.272*r + 0.534*g + 0.131*b),255)
    return [newRed, newGreen, newBlue]

def imagetosepia(im):
    h = len(im)
    w = len(im[0])

    # TODO: multithreading

    for row in range(h):
        for col in range(w):
            sep = pixeltosepia(im[row][col])
            im[row][col] = sep

    newim = Image.fromarray(im, 'RGB')
    return newim

def main():
    argv = sys.argv
    argc = len(argv)

    if argc != 2:
        usage()
        exit(1)

    # TODO: accept multiple files at once

    im = loadimage(argv[1])
    newim = imagetosepia(im)

    newim.save("out.jpg")

if __name__ == '__main__':
    main()
