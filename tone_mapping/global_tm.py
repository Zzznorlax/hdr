
import numpy as np


class GlobalToneMapping():

    @staticmethod
    def gamma_compression(image: np.ndarray, gamma: float = 1.6) -> np.ndarray:
        """applies gamma compression on the HDR image

        Args:
            image (np.ndarray): image to be tone mapped
            gamma (float, optional): gamma coefficient, recommended range is 1.6 ~ 2.2. Defaults to 1.6.

        Returns:
            np.ndarray: image after tone mapping
        """
        image = image ** gamma
        return image

    @staticmethod
    def photographic(image: np.ndarray, key: float = 0.36, d: float = 1e-8) -> np.ndarray:
        """applies photographic tone mapping on the HDR image

        Args:
            image (np.ndarray): image to be tone mapped
            key (float, optional): user specified key. Defaults to 0.36.
            d (float, optional): small value used to prevent ln(0). Defaults to 1e-8.

        Returns:
            np.ndarray: image after tone mapping
        """

        l_avg = np.exp(np.mean(np.log(image + d)))
        l_median = key * image / l_avg

        l_white = np.max(l_median)

        l_display = l_median * (1 + l_median / (l_white ** 2)) / (1 + l_median)

        return l_display
