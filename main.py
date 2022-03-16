from debevec import DebevecMethod

from utils import hdr as hdr_utils

if __name__ == '__main__':
    folder = 'samples/memorial'
    output_dir = folder + '/outputs'

    hdr = DebevecMethod(img_folder=folder, n=50, lc=100)
    hdr.solve_g()
    hdr.plot_g(output_dir + '/g_plots.png')
    hdr.compute_radiance_map()
    hdr.plot_ln_radiance_map(output_dir + '/radiance_map.png')

    hdr.compute_radiance(output_dir + '/r.hdr')

    hdr_utils.write_radiance_map(hdr.radiance_map, dest=output_dir + '/test.hdr')
