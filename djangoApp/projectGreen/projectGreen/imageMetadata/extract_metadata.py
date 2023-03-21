"""
Metadata extraction:
https://www.thepythoncode.com/article/extracting-image-metadata-in-python
GPS data decoding:
https://stackoverflow.com/questions/19804768/interpreting-gps-info-of-exif-data-from-photo-in-python
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from datetime import datetime as dt

def extract_metadata(img: Image) -> dict[dict, dt]:
    '''
    Extracts relevant metadata from an image
    TAGS and GPSTAGS are used to decode int tags to string tags

    Returned GPSInfo dictionary:
        GPSLatitude / GPSLongitude are 3-tuples of float values
        Lat./Long. Refs are characters indicating cardinal direction [N, E, S, W]
        GPSAltitude is a high precision float
    '''
    out = {}
    exif_data = img._getexif() # _getexif is protected method
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'GPSInfo':
            data = exif_data.get(tag_id)
            relevant_tags = ['GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude', 'GPSAltitude']
            out['GPSInfo'] = {}
            for key_id in data:
                key = GPSTAGS.get(key_id, key_id)
                if key in relevant_tags:
                    if isinstance(data[key_id], str):
                        out['GPSInfo'][key] = data[key_id]
                    elif isinstance(data[key_id], tuple):
                        out['GPSInfo'][key] = [float(data[key_id][i]) for i in range(3)]
                    else:
                        out['GPSInfo'][key] = float(data[key_id])
        if tag == 'DateTime':
            date_string = exif_data.get(tag_id)
            out['DateTime'] = dt.strptime(date_string, '%Y:%m:%d %H:%M:%S')
    return out


def extract_metadata_from_filepath(filepath: str) -> dict[dict, dt]:
    '''
    Wrapper for extract_metadata function with filepath input
    '''
    source_image = Image.open(filepath)
    return extract_metadata(source_image)


def coordinates_to_decdegrees(lat:list, lon:list):
    '''
    Convert latitude and longitude coordinates into decimal degrees
    '''
    dd_latitude = lat[0] + (lat[1]/60) + (lat[2]/3600)
    if lat[3] == "S":
        dd_latitude = -dd_latitude
    dd_longitude = lon[0] + (lon[1]/60) + (lon[2]/3600)
    if lon[3] == "W":
        dd_longitude = -dd_longitude
    return (dd_latitude, dd_longitude)


def process_GPS_data(img: Image):
    data = extract_metadata(img)
    gps_info = data['GPSInfo']
    latitude = gps_info['GPSLatitude'] + [gps_info['GPSLatitudeRef']]
    longitude = gps_info['GPSLongitude'] + [gps_info['GPSLongitudeRef']]
    d_lat, d_lon = coordinates_to_decdegrees(latitude, longitude)
    return d_lat, d_lon
    # USE GEOPY to calculate distance in models
    

#source_image = Image.open('IMG_1379.jpg')
#process_GPS_data(source_image)


if __name__ == '__main__':
    source_image = Image.open('IMG_1379.jpg')
    exif_data = source_image._getexif()

    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'MakerNote':
            # skipped as it returns either a
            # UnicodeDecodeError or a long byte string
            continue
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

GDPR note: no other metadata should be extracted/stored unless it is used for the purposes outlined above
"""