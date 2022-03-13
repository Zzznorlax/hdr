from hdr import HDR


if __name__ == '__main__':
    folder = 'samples'
    hdr = HDR(img_folder=folder, n=50, lc=100)
    hdr.solve_g()
    hdr.plot_g()
