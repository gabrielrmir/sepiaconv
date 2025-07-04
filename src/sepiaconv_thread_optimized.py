import sys
import threading
import argparse
from PIL import Image
import numpy as np

def usage():
    print("Usage: sepiaconv.py <file> --threads <num_threads> --subdivs <num_subdivs>")

def load_image(filename):
    try:
        im = Image.open(filename)
    except Exception as e:
        print(f"[ERROR] Could not load image: {e}")
        sys.exit(1)
    return im

def pixel_to_sepia_array(arr):
    """Apply sepia filter to an image array using vectorized operations."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    new_red = np.minimum((0.393 * r + 0.769 * g + 0.189 * b).astype(np.int32), 255)
    new_green = np.minimum((0.349 * r + 0.686 * g + 0.168 * b).astype(np.int32), 255)
    new_blue = np.minimum((0.272 * r + 0.534 * g + 0.131 * b).astype(np.int32), 255)
    return np.stack([new_red, new_green, new_blue], axis=2)

def chunkify(im, subdivs):
    """Divide image into chunks."""
    cells = (subdivs + 1) ** 2
    width = im.width // (subdivs + 1)
    height = im.height // (subdivs + 1)
    chunks = []
    positions = []
    for i in range(cells):
        left = (i % (subdivs + 1)) * width
        top = (i // (subdivs + 1)) * height
        right = left + width
        bottom = top + height
        chunks.append(im.crop((left, top, right, bottom)))
        positions.append((left, top))
    return chunks, positions

def image_to_sepia(im):
    """Convert a chunk to sepia using vectorized operations."""
    arr = np.asarray(im, dtype=np.float32)
    sepia_arr = pixel_to_sepia_array(arr)
    return Image.fromarray(sepia_arr.astype(np.uint8), "RGB")

def chunk_processor(target_im):
    """Process chunks in a thread-safe manner."""
    while True:
        with lock:
            if not data:
                break
            chunk, pos = data.pop()
        sepia = image_to_sepia(chunk)
        with lock:
            target_im.paste(sepia, pos)

def main():
    parser = argparse.ArgumentParser(description="Convert an image to sepia using threads.")
    parser.add_argument("filename", help="Input image file")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use")
    parser.add_argument("--subdivs", type=int, default=3, help="Number of subdivisions per axis")
    args = parser.parse_args()

    im = load_image(args.filename)
    subdivs = args.subdivs
    chunks, positions = chunkify(im, subdivs)
    newim = Image.new("RGB", im.size)

    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=chunk_processor, args=(newim,))
        threads.append(t)

    for chunk, pos in zip(chunks, positions):
        data.append((chunk.copy(), pos))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    newim.save("out.jpg")
    print("Image saved as out.jpg")

lock = threading.Lock()
data = []

if __name__ == "__main__":
    main()

