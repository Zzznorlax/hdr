
from typing import List
import cv2
import numpy as np


R_WEIGHT = 54
G_WEIGHT = 183
B_WEIGHT = 19


def shift_x(img: np.ndarray, n: int, fill_value: int = 0) -> np.ndarray:

    result = np.empty_like(img)

    if n > 0:
        result[:, :n] = fill_value
        result[:, n:] = img[:, :-n]

    elif n < 0:
        result[:, n:] = fill_value
        result[:, :n] = img[:, -n:]

    else:
        result = img

    return result


def shift_y(img: np.ndarray, n: int, fill_value: int = 0) -> np.ndarray:

    result = np.empty_like(img)

    if n > 0:
        result[:n, :] = fill_value
        result[n:, :] = img[:-n, :]

    elif n < 0:
        result[n:, :] = fill_value
        result[:n, :] = img[-n:, :]

    else:
        result = img

    return result


def to_default_format(img: np.ndarray, to_rgb: bool = False) -> np.ndarray:
    """converts image to default dims order (height, width, channels)

    Args:
        img (np.ndarray): image with dims (channels, height, width)
        to_rgb (bool, optional): BGR to RGB. Defaults to False.

    Returns:
        np.ndarray: converted image
    """

    img = np.moveaxis(img, 0, -1)

    if to_rgb:
        img = img[:, :, -1]

    return img


def rgb_to_gray(r: int, g: int, b: int) -> int:
    return (r * R_WEIGHT + g * G_WEIGHT + b * B_WEIGHT) // (R_WEIGHT + G_WEIGHT + B_WEIGHT)


def to_grayscale(img: np.ndarray) -> np.ndarray:

    u_to_grayscale = np.vectorize(rgb_to_gray)

    return u_to_grayscale(img[:, :, 2], img[:, :, 1], img[:, :, 0])


def to_binary(img: np.ndarray, thres: float, high: int = 255, low: int = 0) -> np.ndarray:
    """converts grayscale image to binary

    Args:
        img (np.ndarray): grayscale image
        thres (float): binary threshold
        high (int, optional): value when above threshold. Defaults to 255.
        low (int, optional): value when lower than threshold. Defaults to 0.

    Returns:
        np.ndarray: binary image
    """

    # median threshold binary
    return np.where(img > thres, high, low)


def to_binary_bool(img: np.ndarray, thres: float) -> np.ndarray:
    """converts grayscale image to binary

    Args:
        img (np.ndarray): grayscale image
        thres (float): binary threshold
        high (int, optional): value when above threshold. Defaults to 255.
        low (int, optional): value when lower than threshold. Defaults to 0.

    Returns:
        np.ndarray: binary image
    """

    # median threshold binary
    return np.where(img > thres, True, False)


# XXX under construction
def mtb_alignment(imgs: np.ndarray, denoise_rate: int = 1, scale: int = 9) -> np.ndarray:

    exclusion_maps = []

    mtb_imgs: List[np.ndarray] = []

    for img in imgs:
        gray = to_grayscale(img)
        median = np.median(gray)

        mtb = to_binary(gray, float(median), 1, 0)

        mtb_imgs.append(cv2.resize(mtb.astype(np.float32), dsize=(mtb.shape[0] // (2 ** scale), mtb.shape[1] // (2 ** scale))))

        # creates exclusion map
        exclusion_map = np.where(np.logical_and(np.less_equal(gray, median + denoise_rate), np.greater_equal(gray, median - denoise_rate)), 0, 1)
        exclusion_maps.append(cv2.resize(exclusion_map.astype(np.float32), dsize=(exclusion_map.shape[0] // (2 ** scale), mtb.shape[1] // (2 ** scale))))

    # initializes offsets with [y = 0, x = 0]
    offsets = []
    for _ in range(len(mtb_imgs)):
        offsets.append([0, 0])

    directions = [-1, 0, 1]
    template_idx = len(mtb_imgs) // 2
    for _ in range(scale):

        template = mtb_imgs[template_idx]

        for idx, mtb in enumerate(mtb_imgs):

            if idx == template_idx:
                continue

            diff = np.count_nonzero(template)
            min_offset = [0, 0]
            for offset_x in directions:
                for offset_y in directions:
                    shifted = shift_y(shift_x(mtb, offset_x), offset_y)

                    offset_diff = np.count_nonzero(np.logical_and(np.logical_xor(shifted, template), exclusion_maps[idx]))
                    if diff > offset_diff:
                        diff = offset_diff
                        min_offset = [offset_y, offset_x]

            # shifts and scales image
            mtb = shift_y(shift_x(mtb, min_offset[1]), min_offset[0])
            mtb_imgs[idx] = cv2.resize(mtb, dsize=(mtb.shape[0] * 2, mtb.shape[1] * 2), interpolation=cv2.INTER_LINEAR)
            exclusion_maps[idx] = cv2.resize(exclusion_maps[idx], dsize=(exclusion_maps[idx].shape[0] * 2, exclusion_maps[idx].shape[1] * 2), interpolation=cv2.INTER_LINEAR)

            offsets[idx][0] = offsets[idx][0] * 2 + min_offset[0]
            offsets[idx][1] = offsets[idx][1] * 2 + min_offset[1]

        mtb_imgs[template_idx] = cv2.resize(template, dsize=(template.shape[0] * 2, template.shape[1] * 2), interpolation=cv2.INTER_LINEAR)
        exclusion_maps[template_idx] = cv2.resize(exclusion_maps[template_idx], dsize=(exclusion_maps[template_idx].shape[0], exclusion_maps[template_idx].shape[1]), interpolation=cv2.INTER_LINEAR)

    for idx, img in enumerate(imgs):
        imgs[idx] = shift_y(shift_x(img, offsets[idx][1]), offsets[idx][0])

    return imgs
