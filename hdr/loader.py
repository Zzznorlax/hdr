
from typing import Optional
from PIL import Image
import numpy as np

from utils import file as file_utils
from utils import exif as exif_utils
from utils import log as log_utils
from utils import image as img_utils


class ImageLoader():

    def __init__(self, dir: str, align_scale: Optional[int] = 5):

        self.EXTS = ['.jpg', '.png', '.jpeg', '.JPG']

        stdout_handler = log_utils.get_stream_handler()
        self.logger = log_utils.get_logger(name="image-loader-logger", handlers=[stdout_handler])

        self.logger.info("start loading images in {}".format(dir))

        self.exposure_time = []

        file_paths = file_utils.get_files(dir)

        imgs = []
        for file_path in file_paths:
            filename, ext = file_utils.get_extension(file_path)

            if ext not in self.EXTS:
                continue

            self.logger.info("{} found".format(file_path))

            img = self.load_image(file_path)

            self.exposure_time.append(self.parse_exposure_time(img, filename))
            imgs.append(np.array(img))

        self.imgs = np.array(imgs)

        # aligns images
        if align_scale is not None:
            self.logger.info("start MTB image alignment for {} images with scale set to {}".format(len(self.imgs), align_scale))
            self.imgs = img_utils.mtb_alignment(self.imgs, scale=align_scale)

    @staticmethod
    def load_image(path: str) -> Image.Image:
        return Image.open(path).convert('RGB')

    @staticmethod
    def parse_exposure_time(img: Image.Image, filename: str) -> float:

        d_t: float = 0

        try:
            exif = exif_utils.parse_exif(img)
            d_t = float(exif['ExposureTime'])

        except KeyError:
            filename, _ = file_utils.get_extension(filename)
            filename = filename.replace('_', '/')
            d_t = eval(filename)

        return d_t
