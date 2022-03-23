# High Dynamic Range Imaging

### TODO
- [ ] 繳交檔案 hw1_[teamID].zip e.g. hw1_[30].zip
- [ ] data/
    - [ ] a. 原始照片（original pictures for a scene under different exposures）
    - [ ] b. recovered HDR image
    - [ ] c. tone-mapped image
- [x] code/
  - [x] Main args parsing
    請提供你們小組的所有程式碼(若有可執行檔案請一併附上)
- [x] README
    請描述程式執行方式/dependency等，並確保程式能夠執行
- [ ] report.pdf/html
    請繳交pdf或html格式，描述：
    - [ ] 作業內容
    - [ ] 實作演算法
    - [ ] 實作細節
    - [ ] 實作結果
    請特別注意：若有實作加分項目(詳細項目請參考作業詳細內容)，請務必在report描述並註明
- [ ] result.png
    最終結果圖，該圖為你們小組最終的實作結果且會用於投票中，投票結果前五名的組別會有額外加分


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
python3 main.py --data path/to/images
```

| Arguments             |    Default    | Description                           |
| :-------------------- | :-----------: | :------------------------------------ |
| --data                | samples/data  | input images directory                |
| --align               |       5       | align input images with given scale   |
| --lambda              |      100      | smoothing coefficient                 |
| --sample-num          | 512 / img_num | sample pixel number                   |
| --plot-g              |     True      | plot g function                       |
| --plot-radiance       |     True      | plot radiance map                     |
| --global-photographic |     0.36      | global photographic tone mapping      |
| --gamma-compression   |      1.6      | global gamma compression tone mapping |

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
  <img src="assets/pre_alignment.png" alt="before alignment"/>

* After alignment
  <img src="assets/aligned.png" alt="aligned"/>
