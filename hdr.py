import math
import random
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
        self.z_range_length = self.MAX_VAL - self.MIN_VAL + 1

        # image count
        self.P = 0

        # sample pixel count
        self.N = n

        # image size
        self.W = 0
        self.H = 0

        self.L: float = lc

        self.ch_num = 3

        # list of g functions in r, g, b order
        self.G = np.zeros((self.ch_num, self.z_range_length))

        # Images as numpy array
        self.imgs: List[np.ndarray] = []

        # List of log(Exposure time)
        self.exposure_time: List[float] = []
        self.load_folder(img_folder)

        # rearrange image layers channel-wisely
        # shape: [channels, images num, height, width]
        self.layers = np.zeros((self.ch_num, self.P, self.H, self.W), dtype=np.uint8)
        for i in range(self.ch_num):
            self.layers[i] = np.array([img[:, :, i] for img in self.imgs])
            # np.savetxt('sample_a.txt', self.layers[i][0])
        self.samples = np.zeros((self.ch_num, self.N, self.P), dtype=np.uint8)
        self.sample()

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
            self.H = np_img.shape[0]
            self.W = np_img.shape[1]

            self.imgs.append(np_img)

        self.P = len(self.imgs)

    @staticmethod
    def load_image(path: str) -> Image.Image:
        return Image.open(path).convert('RGB')

    def read_exposure_time(self, img: Image.Image) -> float:
        exif = exif_utils.parse_exif(img)
        return float(exif[self.EXPOSURE_TIME_KEY])

    def sample(self):

        step = math.ceil((self.MAX_VAL - self.MIN_VAL + 1) / self.N)

        for ch_idx in range(self.ch_num):
            sample_layer = self.layers[ch_idx, self.P // 2, :, :]

            # randomly samples from points in sample_layer where value == z
            sample_idx = 0
            for z in range(self.MIN_VAL, self.MAX_VAL, step):
                ys, xs = np.where(sample_layer == z)

                if len(ys) == 0:
                    continue

                sample_pos_idx = random.randrange(len(ys))

                self.samples[ch_idx][sample_idx] = self.layers[ch_idx, :, ys[sample_pos_idx], xs[sample_pos_idx]]
                sample_idx += 1

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

    def solve_g(self):

        z_range_length = self.MAX_VAL - self.MIN_VAL + 1
        row_num = self.N * self.P + 1 + z_range_length - 2
        col_num = z_range_length + self.N

        for ch in range(self.ch_num):

            mat_a = np.zeros((row_num, col_num))
            mat_b = np.zeros((row_num))

            row_idx = 0

            # composes upper part
            for sample_idx, samples in enumerate(self.samples[ch]):
                for pic_idx, z in enumerate(samples):
                    w_z = self.weighting(z)
                    mat_a[row_idx][z] = 1 * w_z
                    mat_a[row_idx][z_range_length + sample_idx] = -1 * w_z
                    mat_b[row_idx] = self.exposure_time[pic_idx] * w_z
                    row_idx += 1

            # add constraint for g_mid == 0
            mat_a[row_idx][(z_range_length) // 2] = 1
            # b[row_idx] = 0
            row_idx += 1

            # composes lower part
            for i in range(1, z_range_length - 1):
                w_z = self.weighting(i)
                mat_a[row_idx][i - 1] = 1 * self.L * w_z
                mat_a[row_idx][i] = -2 * self.L * w_z
                mat_a[row_idx][i + 1] = 1 * self.L * w_z
                # b[row_idx] = 0
                row_idx += 1

            # solves Ax = b
            x = np.linalg.lstsq(mat_a, mat_b)

            self.G[ch] = x[0][self.MIN_VAL:self.MAX_VAL + 1]

    def plot_g(self):
        label_list = ['R', 'G', 'B']
        marker_list = ['r--', 'g', 'b']
        for idx, data in enumerate(self.G):
            plt.subplot(2, 2, idx + 1)
            plt.title(label_list[idx])
            plt.plot(data[:], marker_list[idx])
            plt.xticks([])
            plt.yticks([])

            plt.subplot(2, 2, 4)
            plt.title(label_list[idx])
            plt.plot(data[:], marker_list[idx])
            plt.xticks([])
            plt.yticks([])

        plt.show()
