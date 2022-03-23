import math
import random
import numpy as np
import matplotlib.pyplot as plt

from typing import List, Optional

from . import loader
from utils import log as log_utils
from utils import hdr as hdr_utils


class DebevecMethod():

    def __init__(self, img_loader: loader.ImageLoader, n: Optional[int] = None, lc: float = 5):

        stdout_handler = log_utils.get_stream_handler()
        self.logger = log_utils.get_logger("debevec-logger", handlers=[stdout_handler])

        self.logger.info("Initializing Debevec Method")
        self.logger.info("lambda: {}".format(lc))

        self.MAX_VAL = 255
        self.MIN_VAL = 0
        self.z_range_length = self.MAX_VAL - self.MIN_VAL + 1

        self.weighting_ufunc = np.vectorize(self.weighting)

        self.L: float = lc

        self.ch_num = 3

        self.img_paths = []

        # ndarray of g functions in r, g, b order
        self.G = np.zeros((self.ch_num, self.z_range_length))

        # images as numpy array
        self.imgs = img_loader.imgs

        # image size
        self.H = self.imgs[0].shape[0]
        self.W = self.imgs[0].shape[1]

        # number of pictures
        self.P = len(self.imgs)
        self.logger.info("picture number: {}".format(self.P))

        # sample pixel count
        if n is None:
            n = (self.MAX_VAL - self.MIN_VAL) * 2 // self.P
        self.N = n
        self.logger.info("sample pixel number: {}".format(self.N))

        # radiance map
        self.radiance_map = np.zeros((self.ch_num, self.H, self.W), dtype=np.float32)

        # list of ln(Exposure time)
        self.exposure_time: List[float] = [math.log(d_t) for d_t in img_loader.exposure_time]

        self.logger.info("image size: {} x {}".format(self.W, self.H))

        # single channel image layers
        # shape: [channels, images num, height, width]
        self.layers = np.zeros((self.ch_num, self.P, self.H, self.W), dtype=np.uint8)
        for i in range(self.ch_num):
            self.layers[i] = np.array([img[:, :, i] for img in self.imgs])

        self.samples = np.zeros((self.ch_num, self.N, self.P), dtype=np.uint8)
        self.sample()

    def sample(self):

        # uniformly samples from z in range 0 ~ 255
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

        self.logger.info("sample number: {} x {} x {} = {}".format(self.ch_num, self.P, self.N, self.ch_num * self.P * self.N))

    # W func
    def weighting(self, val):
        """hat weighting function
        """

        if val >= (self.MAX_VAL + self.MIN_VAL) / 2:
            return self.MAX_VAL - val

        return val - self.MIN_VAL

    def solve_g(self):
        self.logger.info("start solving g")
        z_range_length = self.MAX_VAL - self.MIN_VAL + 1
        row_num = self.N * self.P + 1 + z_range_length - 2
        col_num = z_range_length + self.N

        for ch in range(self.ch_num):
            self.logger.info("solving g for channel {}".format(ch))

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
            x = np.linalg.lstsq(mat_a, mat_b, rcond=None)

            self.G[ch] = x[0][self.MIN_VAL:self.MAX_VAL + 1]

        self.logger.info("g solved")

    def compute_radiance_map(self, dest: Optional[str] = None):
        self.logger.info("start constructing radiance map")

        # with float32 opencv can then save radiance map as .hdr file
        tmp = np.zeros((self.ch_num, self.P, self.H, self.W), dtype=np.float32)

        # w(zij) * (g(zij) - ln(tj))
        for ch in range(self.ch_num):
            tmp[ch] += self.G[ch][self.layers[ch]]

        for pic_idx in range(self.P):
            tmp[:, pic_idx, :, :] -= self.exposure_time[pic_idx]

        weighted_z = self.weighting_ufunc(self.layers)

        tmp *= weighted_z

        # weighted average
        # adds 1e-8 before division to prevent divided by zeros
        tmp = np.sum(tmp, axis=1, dtype=np.float32) / (np.sum(weighted_z, axis=1, dtype=np.float32) + 1e-8)

        # restores radiance from ln(radiance)
        self.radiance_map = np.exp(tmp)

        self.logger.info("radiance map constructed")

        if dest is not None:
            hdr_utils.write_hdr(self.radiance_map, dest=dest)
            self.logger.info("HDR image saved to {}".format(dest))

    def plot_ln_radiance_map(self, dest: str):
        label_list = ['R', 'G', 'B', 'Image']
        for idx in range(self.ch_num):
            plt.subplot(2, 2, idx + 1)
            plt.title(label_list[idx])
            plt.imshow(np.log(self.radiance_map[idx]), interpolation='none')
            plt.xticks([])
            plt.yticks([])

        plt.subplot(2, 2, 4)
        plt.title(label_list[3])
        plt.imshow(self.imgs[self.P // 2])
        plt.xticks([])
        plt.yticks([])

        plt.savefig(dest, dpi=512)

        self.logger.info("radiance map written to {}".format(dest))

    def plot_g(self, dest: str):
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

        plt.savefig(dest)

        self.logger.info("g plot written to {}".format(dest))
