import argparse
from os.path import join

from hdr.debevec import DebevecMethod
from hdr.loader import ImageLoader
from tone_mapping.global_tm import GlobalToneMapping

from utils import hdr as hdr_utils
from utils import file as file_utils


DEFAULT_DIR = 'samples/data'


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default=DEFAULT_DIR, help='input images directory')
    parser.add_argument('--align', type=int, nargs='?', const=5, help='align input images with scale')
    parser.add_argument('--lc', type=int, default=100, help='smoothing coefficient lambda')
    parser.add_argument('--sample-num', type=int, nargs='?', const=75, help='sample pixel number')
    parser.add_argument('--plot-g', type=bool, nargs='?', const=True, default=True, help='plot g')
    parser.add_argument('--plot-radiance', type=bool, nargs='?', const=True, default=True, help='plot radiance map')
    parser.add_argument('--global-photographic', type=float, nargs='?', const=0.36, help='global photographic tone mapping')
    parser.add_argument('--gamma-compression', type=float, nargs='?', const=1.6, help='global gamma compression tone mapping')

    opt = parser.parse_args()

    return opt


def main(opt: argparse.Namespace):

    data_dir = opt.data
    output_dir = file_utils.create_folder(data_dir, "outputs")

    # loads images
    img_loader = ImageLoader(data_dir, opt.align)

    # assembles HDR image
    hdr = DebevecMethod(img_loader=img_loader, n=opt.sample_num, lc=opt.lc)
    hdr.solve_g()
    hdr.compute_radiance_map(dest=join(output_dir, "raw.hdr"))

    if opt.plot_g:
        hdr.plot_g(join(output_dir, "g_plots.png"))

    if opt.plot_radiance:
        hdr.plot_ln_radiance_map(join(output_dir, "radiance_map.png"))

    if isinstance(opt.global_photographic, float):
        key = opt.global_photographic
        img = GlobalToneMapping.photographic(hdr.radiance_map, key=key)

        key_str = str(key).replace(".", "_")
        hdr_utils.write_hdr(img, join(output_dir, "tm_photographic_{}.hdr".format(key_str)))

    if isinstance(opt.gamma_compression, float):
        gamma = opt.gamma_compression
        img = GlobalToneMapping.gamma_compression(hdr.radiance_map, gamma=gamma)

        gamma_str = str(gamma).replace(".", "_")
        hdr_utils.write_hdr(img, join(output_dir, "tm_gamma_{}.hdr".format(gamma_str)))


if __name__ == '__main__':

    opt = parse_opt()

    main(opt)
