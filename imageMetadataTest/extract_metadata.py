"""
Metadata extraction:
https://www.thepythoncode.com/article/extracting-image-metadata-in-python
GPS data decoding:
https://stackoverflow.com/questions/19804768/interpreting-gps-info-of-exif-data-from-photo-in-python
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

if __name__ == '__main__':
    source_image = Image.open('IMG_1379.jpg')
    exif_data = source_image._getexif() # _getexif is protected method

    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'MakerNote':
            continue # skipped as it returns either a UnicodeDecodeError or a long byte string
        data = exif_data.get(tag_id)
        if isinstance(data, bytes):
            data = data.decode()
        if tag == 'GPSInfo':
            print('GPSInfo')
            for key_id in data:
                key = GPSTAGS.get(key_id, key_id)
                print('    {0:21}: {1}'.format(key, data[key_id]))
        else:
            print('{0:25}: {1}'.format(tag, data))

"""
DateTime can be used to check if the photo was taken
    (a) after the challenge is set and
    (b) within the time window
GPSInfo contains data which can be used to check location-specific challenges

GDPR note: no other metadata should be extracted/stored unless it is used for the purposes outliuned above
"""