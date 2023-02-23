import pytest
from PIL import Image
from datetime import datetime as dt

from extract_metadata import extract_metadata, extract_metadata_from_filepath

TEST_IMG_FILEPATH = 'IMG_1379.jpg'
CARDINAL = ['N', 'E', 'S', 'W']

def test_extract_metatdata():
    source_img = Image.open(TEST_IMG_FILEPATH)
    output = extract_metadata(source_img)
    print(output['DateTime'])
    assert type(output['DateTime']) == dt

    assert output['GPSInfo']['GPSLatitudeRef'] in CARDINAL
    assert output['GPSInfo']['GPSLongitudeRef'] in CARDINAL

    assert len(output['GPSInfo']['GPSLatitude']) == 3
    assert len(output['GPSInfo']['GPSLongitude']) == 3
    print(type(output['GPSInfo']['GPSLongitude'][0]))
    print(float(output['GPSInfo']['GPSAltitude']))
    assert type(output['GPSInfo']['GPSAltitude']) == float

def test_extract_metadata_from_filepath():
    source_img = Image.open(TEST_IMG_FILEPATH)
    output = extract_metadata(source_img)
    assert extract_metadata_from_filepath(TEST_IMG_FILEPATH) == output