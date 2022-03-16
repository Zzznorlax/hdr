from hdr.debevec import DebevecMethod
from tone_mapping.global_tm import GlobalToneMapping

from utils import hdr as hdr_utils

if __name__ == '__main__':
    folder = 'samples/memorial'
    output_dir = folder + '/outputs'

    # hdr = DebevecMethod(img_folder=folder, n=50, lc=100)
    # hdr.solve_g()
    # hdr.plot_g(output_dir + '/g_plots.png')
    # hdr.compute_radiance_map()
    # hdr.plot_ln_radiance_map(output_dir + '/radiance_map.png')

    # hdr_utils.write_hdr(hdr.radiance_map, dest=output_dir + '/test.hdr')

    img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    img = GlobalToneMapping.photographic(img, key=0.27)
    hdr_utils.write_hdr(img, output_dir + '/tm_photographic_27.hdr')
