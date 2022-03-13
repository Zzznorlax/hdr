import math
import numpy as np
import matplotlib.pyplot as plt

from typing import List
from PIL import Image


from utils import file as file_utils
from utils import exif as exif_utils


class HDR():

    def __init__(self, img_folder: str, n: int = 50, lc: float = 5):
        self.EXPOSURE_TIME_KEY = 'ExposureTime'
        self.EXTS = ['.jpg', '.png', '.jpeg']
        self.MAX_VAL = 255
        self.MIN_VAL = 0

        # image count
        self.P = 0

        # sample pixel count
        self.N = n

        # list of g functions in r, g, b order
        self.G: List[np.ndarray] = []

        self.L: float = lc

        # Images as numpy array
        self.imgs: List[np.ndarray] = []
        self.ch_r: List[np.ndarray] = []
        self.ch_g: List[np.ndarray] = []
        self.ch_b: List[np.ndarray] = []

        # List of log(Exposure time)
        self.exposure_time: List[float] = []
        self.load_folder(img_folder)

    # TODO Add size check
    def load_folder(self, path: str):
        file_paths = file_utils.get_files(path)

        for file_path in file_paths:
            name, ext = file_utils.get_extension(file_path)
            name = file_utils.get_filename(name)
            if ext not in self.EXTS:
                continue

            img = Image.open(file_path).convert('RGB')

            try:
                d_t = self.read_exposure_time(img)
                print("{}: exposure time = {}".format(file_path, d_t))

            except KeyError:
                d_t = 1 / int(name)

            self.exposure_time.append(math.log10(d_t))
            np_img = np.array(img)

            self.imgs.append(np_img)

            step = math.ceil(np_img.shape[0] * np_img.shape[1] / self.N)

            # separates channels -> reshapes to 1D -> samples N points
            self.ch_r.append(np_img[:, :, 0].ravel()[0:-1:step])
            self.ch_g.append(np_img[:, :, 1].ravel()[0:-1:step])
            self.ch_b.append(np_img[:, :, 2].ravel()[0:-1:step])

            self.P += 1

    # W func
    def weighting(self, val: float) -> float:
        """hat weighting function

        Args:
            val (float): _description_
            upper (float): _description_
            lower (float): _description_

        Returns:
            float: _description_
        """

        if val >= (self.MAX_VAL + self.MIN_VAL) / 2:
            return self.MAX_VAL - val

        return val - self.MIN_VAL

    @staticmethod
    def load_image(path: str) -> Image.Image:
        return Image.open(path).convert('RGB')

    def read_exposure_time(self, img: Image.Image) -> float:
        exif = exif_utils.parse_exif(img)
        return float(exif[self.EXPOSURE_TIME_KEY])

    def solve_g(self):

        z_range_length = self.MAX_VAL - self.MIN_VAL + 1

        for ch in [self.ch_r, self.ch_g, self.ch_b]:
            row_num = self.N * self.P + 1 + z_range_length - 2
            col_num = z_range_length + self.N
            a = np.zeros((row_num, col_num))
            b = np.zeros((row_num))

            row_idx = 0
            # composes upper part
            for pic_idx, p in enumerate(ch):
                for z in p:
                    w_z = self.weighting(z)
                    a[row_idx][z] = 1 * w_z
                    a[row_idx][z_range_length + pic_idx] = -1 * w_z
                    b[row_idx] = self.exposure_time[pic_idx] * w_z
                    row_idx += 1

            # add constraint for g_mid == 0
            a[row_idx][(z_range_length) // 2] = 1
            # b[row_idx] = 0
            row_idx += 1

            # composes lower part
            for i in range(1, z_range_length - 1):
                w_z = self.weighting(i)
                a[row_idx][i - 1] = 1 * self.L * w_z
                a[row_idx][i] = -2 * self.L * w_z
                a[row_idx][i + 1] = 1 * self.L * w_z
                # b[row_idx] = 0
                row_idx += 1

            # solves Ax = b
            # np.savetxt('B.txt', b)
            # x = np.linalg.lstsq(a, b)

            inv_a = np.linalg.pinv(a)
            x = np.dot(inv_a, b)

            g = x[0: z_range_length]
            print(g)
            self.G.append(g)
            # self.G.append(x[0][0:z_range_length])
            # print(len(x[0]), x[0][self.MIN_VAL:self.MAX_VAL + 1])

    def plot_g(self):
        label_list = ['R', 'G', 'B']
        for idx, data in enumerate(self.G):
            plt.subplot(2, 2, idx + 1)
            plt.title(label_list[idx])
            plt.plot(data[:])
            plt.xticks([])
            plt.yticks([])
        plt.show()

    # def compute_radiance_map(self) -> float:

    #     m = np.array([])
    #     for idx, img in enumerate(self.imgs):
    #         for ch in range(3):
    #             m = np.append(m, self.weighting(self.g(img) - self.exposure_time[idx]))
