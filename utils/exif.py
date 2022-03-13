
from typing import Dict
from PIL import Image
from PIL.ExifTags import TAGS


def parse_exif(img: Image.Image) -> Dict[str, str]:

    exif = img.getexif()
    exif = exif.get_ifd(0x8769)
    exif_dict = {}

    for tag_id in exif:
        tag = TAGS.get(tag_id, tag_id)
        content = exif.get(tag_id)
        exif_dict[tag] = content

    return exif_dict


if __name__ == '__main__':
    image = Image.open('samples/minus_2.jpg').convert('L')

    exif = parse_exif(image)
    print(exif['ExposureTime'])
