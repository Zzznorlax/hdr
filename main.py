from hdr.debevec import DebevecMethod
from tone_mapping.global_tm import GlobalToneMapping

from utils import hdr as hdr_utils
from utils import file as file_utils

if __name__ == '__main__':
    folder = 'samples/roof_3'

    output_dir = file_utils.create_folder(folder, "outputs")

    hdr = DebevecMethod(img_folder=folder, n=50, lc=100)
    hdr.solve_g()
    hdr.plot_g(output_dir + '/g_plots.png')
    hdr.compute_radiance_map()
    hdr.plot_ln_radiance_map(output_dir + '/radiance_map.png')

    hdr_utils.write_hdr(hdr.radiance_map, dest=output_dir + '/raw.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.photographic(raw_img, key=0.36)
    # hdr_utils.write_hdr(img, output_dir + '/tm_photographic_36.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.gamma_compression(raw_img, gamma=2.2)
    # hdr_utils.write_hdr(img, output_dir + '/tm_gamma_22.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.photographic(raw_img, key=0.28)
    # hdr_utils.write_hdr(img, output_dir + '/tm_photographic_28.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.gamma_compression(raw_img, gamma=1.8)
    # hdr_utils.write_hdr(img, output_dir + '/tm_gamma_18.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.photographic(raw_img, key=0.16)
    # hdr_utils.write_hdr(img, output_dir + '/tm_photographic_16.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.gamma_compression(raw_img, gamma=1.6)
    # hdr_utils.write_hdr(img, output_dir + '/tm_gamma_16.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.photographic(raw_img, key=0.16)
    # hdr_utils.write_hdr(img, output_dir + '/tm_photographic_16.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.gamma_compression(raw_img, gamma=1.2)
    # hdr_utils.write_hdr(img, output_dir + '/tm_gamma_12.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.photographic(raw_img, key=0.12)
    # hdr_utils.write_hdr(img, output_dir + '/tm_photographic_12.hdr')

    # raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    # img = GlobalToneMapping.gamma_compression(raw_img, gamma=0.8)
    # hdr_utils.write_hdr(img, output_dir + '/tm_gamma_08.hdr')
