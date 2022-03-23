import cv2
import numpy as np


def read_hdr(src: str) -> np.ndarray:
    """reads a .hdr file

    Args:
        src (str): file path

    Returns:
        np.ndarray: np.array((channel, height, width)) radiance map
    """

    img = cv2.imread(src, flags=cv2.IMREAD_ANYDEPTH)

    # BGR to RGB
    img = img[:, :, ::-1]

    img = np.moveaxis(img, -1, 0)

    return img


def write_hdr(image: np.ndarray, dest: str):
    """writes radiance map to .hdr file

    Args:
        image (np.ndarray): np.array((channel, height, width), dtype=float32) radiance map
        dest (str): file destination
    """
    # converts image to np.array((height, width, channel))
    image = np.moveaxis(image, 0, -1)

    # RGB to BGR
    image = image[:, :, ::-1]

    cv2.imwrite(dest, image)


def write_rgbe(image: np.ndarray, dest: str):
    """writes radiance map to file in RGBE format

    Args:
        image (np.ndarray): np.array((channel, height, width), dtype=float32) radiance map
        dest (str): file destination
    """

    # converts image to np.array((height, width, channel))
    image = np.moveaxis(image, 0, -1)

    # RGB to BGR
    image = image[:, :, ::-1]

    with open(dest, 'wb') as f:
        encoding = 'ascii'
        f.write(str.encode("#?RADIANCE\n", encoding=encoding))
        f.write(str.encode('# Made with Python & Numpy\n', encoding=encoding))
        f.write(str.encode('FORMAT=32-bit_rle_rgbe\n\n', encoding=encoding))

        f.write(str.encode("-Y {0} +X {1}\n".format(image.shape[0], image.shape[1]), encoding=encoding))

        brightest = np.maximum(np.maximum(image[..., 0], image[..., 1]), image[..., 2])
        mantissa = np.zeros_like(brightest)
        exponent = np.zeros_like(brightest)

        np.frexp(brightest, mantissa, exponent)
        scaled_mantissa = mantissa * 256.0 / brightest
        rgbe = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        rgbe[..., 0:3] = np.around(image[..., 0:3] * scaled_mantissa[..., None])
        rgbe[..., 3] = np.around(exponent + 128)

        rgbe.tofile(f)


def norm_rgb(r, g, b):  # normalize by each color for human vision sensitivity
    return r * 0.216 + g * 0.7152 + b * 0.0722


def to_ldr(src: str, dest: str):
    hdr_img = cv2.imread(src, cv2.IMREAD_ANYDEPTH)

    ldr_img = np.clip(hdr_img * 255, 0, 255).astype('uint8')

    cv2.imwrite(dest, ldr_img)
