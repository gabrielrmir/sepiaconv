import sys
import threading
import argparse
from PIL import Image
import numpy as np
import os

def usage():
    """Exibe a mensagem de uso do programa."""
    print("Usage: sepiaconv.py <file> --threads <num_threads> --subdivs <num_subdivs>")

def load_image(filename):
    """Carrega a imagem do arquivo especificado."""
    try:
        im = Image.open(filename)
    except Exception as e:
        print(f"[ERROR] Could not load image: {e}")
        sys.exit(1)
    return im

def pixel_to_sepia_array(arr):
    """
    Aplica o filtro sépia a um array de imagem usando operações vetorizadas.
    O array de entrada tem formato (altura, largura, 3), onde a última dimensão
    representa os canais RGB: 0=vermelho, 1=verde, 2=azul.
    """
    # Extrai os canais de cor individuais
    red_channel = arr[:, :, 0]  # Todos os pixels, canal vermelho (índice 0)
    green_channel = arr[:, :, 1]  # Todos os pixels, canal verde (índice 1)
    blue_channel = arr[:, :, 2]  # Todos os pixels, canal azul (índice 2)

    # Aplica a transformação sépia
    new_red = np.minimum((0.393 * red_channel + 0.769 * green_channel + 0.189 * blue_channel).astype(np.int32), 255)
    new_green = np.minimum((0.349 * red_channel + 0.686 * green_channel + 0.168 * blue_channel).astype(np.int32), 255)
    new_blue = np.minimum((0.272 * red_channel + 0.534 * green_channel + 0.131 * blue_channel).astype(np.int32), 255)

    # Combina os novos canais em um array 3D
    return np.stack([new_red, new_green, new_blue], axis=2)

def chunkify(im, subdivs):
    """Divide a imagem em pedaços menores."""
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
    """Converte um pedaço da imagem para sépia usando operações vetorizadas."""
    arr = np.asarray(im, dtype=np.float32)
    sepia_arr = pixel_to_sepia_array(arr)
    return Image.fromarray(sepia_arr.astype(np.uint8), "RGB")

def chunk_processor(target_im):
    """Processa pedaços da imagem de forma segura para threads."""
    while True:
        with lock:
            if not data:
                break
            chunk, pos = data.pop()
        sepia = image_to_sepia(chunk)
        with lock:
            target_im.paste(sepia, pos)

def main():
    """Função principal que coordena o processamento da imagem."""
    parser = argparse.ArgumentParser(description="Converte uma imagem para sépia usando threads.")
    parser.add_argument("filename", help="Arquivo de imagem de entrada")
    parser.add_argument("--threads", type=int, default=4, help="Número de threads a usar")
    parser.add_argument("--subdivs", type=int, default=3, help="Número de subdivisões por eixo")
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

    output_filename = "output_" + os.path.basename(args.filename)
    newim.save(output_filename)
    print("Image saved as \"" + output_filename + "\"")

lock = threading.Lock()
data = []

if __name__ == "__main__":
    main()
