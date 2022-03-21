# High Dynamic Range Imaging


### Environment

* Install dependencies
  ```shell
  pip3 install -r requirements.txt
  ```

### Input Format
A folder of images with extensions `.jpg`, `.jpeg`, `.JPG`, `.png` will be loaded as input.
If `ExposureTime` key is not presented in the image's `exif`, image filename will be used for exposure time parsing.
Filename for a `1 / 64` exposure time image should be `1_64.jpg`, with `/` replaced with `_`.
Example for a set of input images could be as following.
```
dir
└── samples
    ├── 2.jpg
    ├── 1.jpg
    ├── 1_2.jpg
    ├── 1_4.jpg
    ├── 1_16.jpg
    └── 1_64.jpg
```

### Usage Example
```python3
from hdr.debevec import DebevecMethod
from tone_mapping.global_tm import GlobalToneMapping

from utils import hdr as hdr_utils
from utils import file as file_utils

    folder = 'samples'

    output_dir = file_utils.create_folder(folder, "outputs")

    hdr = DebevecMethod(img_folder=folder, n=50, lc=100)
    hdr.solve_g()
    hdr.plot_g(output_dir + '/g_plots.png')
    hdr.compute_radiance_map()
    hdr.plot_ln_radiance_map(output_dir + '/radiance_map.png')

    hdr_utils.write_hdr(hdr.radiance_map, dest=output_dir + '/raw.hdr')

    raw_img = hdr_utils.read_hdr(output_dir + '/raw.hdr')
    img = GlobalToneMapping.photographic(raw_img, key=0.36)
    hdr_utils.write_hdr(img, output_dir + '/tm_photographic_36.hdr')
```


### Median Threshold Binary (MTB) Image Alignment
![Before alignment]([url-to-image](https://github.com/Zzznorlax/hdr/blob/main/resource/pre_alignment.png))
![Result]([url-to-image](https://github.com/Zzznorlax/hdr/blob/main/resource/aligned.png))
