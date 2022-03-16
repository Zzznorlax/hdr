import cv2
import numpy as np


def write_radiance_map(image: np.ndarray, dest: str):
    # Assumes you have a np.array((3, height, width), dtype=float) as your HDR image

    # converts image to np.array((height, width, channel))
    image = np.moveaxis(image, 0, -1)

    # RGB to BGR
    image = image[:, :, ::-1]

    cv2.imwrite(dest, image)

    # with open(dest, 'wb') as f:
    #     encoding = 'ascii'
    #     f.write(str.encode("#?RADIANCE\n", encoding=encoding))
    #     f.write(str.encode('# Made with Python & Numpy\n', encoding=encoding))
    #     f.write(str.encode('FORMAT=32-bit_rle_rgbe\n\n', encoding=encoding))

    #     f.write(str.encode("-Y {0} +X {1}\n".format(image.shape[0], image.shape[1]), encoding=encoding))

    #     brightest = np.maximum(np.maximum(image[..., 0], image[..., 1]), image[..., 2])
    #     mantissa = np.zeros_like(brightest)
    #     exponent = np.zeros_like(brightest)

    #     np.frexp(brightest, mantissa, exponent)
    #     scaled_mantissa = mantissa * 256.0 / brightest
    #     rgbe = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    #     rgbe[..., 0:3] = np.around(image[..., 0:3] * scaled_mantissa[..., None])
    #     rgbe[..., 3] = np.around(exponent + 128)
    #     # rgbe[scaled_mantissa < 1e-32, :] = 0

    #     # rgbe.flatten().tofile(f)
    #     rgbe.tofile(f)


def norm_rgb(r, g, b):  # normalize by each color for human vision sensitivity
    return r * 0.216 + g * 0.7152 + b * 0.0722
