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
project_dir
└── samples
    └── data
        ├── 2.jpg
        ├── 1.jpg
        ├── 1_2.jpg
        ├── 1_4.jpg
        ├── 1_16.jpg
        └── 1_64.jpg
```

### Assembling HDR Image
Execute `main.py`.
```shell
python3 main.py
```
This will assemble a HDR image named `raw.hdr`, a plot of g functions in RGB channels `g_plots.png` and
a radiance map `radiance_map.png` in the `outputs` directory.
```
project_dir
└── samples
    └── data
        ├── 1_2.jpg
        ├── 1_4.jpg
        └── outputs
            ├── raw.hdr
            ├── radiance_map.png
            └── g_plots.png
```

### Median Threshold Bitmap (MTB) Image Alignment
Image alignment using median threshold bitmap (MTB) method.
* Before alignment
  ![Before alignment](https://github.com/Zzznorlax/hdr/blob/main/resource/pre_alignment.png)

* After alignment
  ![Result](https://github.com/Zzznorlax/hdr/blob/main/resource/aligned.png)
