import pytest
from PIL import Image
from datetime import datetime as dt
import os

from extract_metadata import extract_metadata, extract_metadata_from_filepath

TEST_IMG_FILEPATH = 'IMG_1379.JPG'
CARDINAL = ['N', 'E', 'S', 'W']

def test_extract_metadata():
    print(os.listdir(os.getcwd()))
    source_img = Image.open(TEST_IMG_FILEPATH)
    output = extract_metadata(source_img)
    assert type(output['DateTime']) == dt

    assert output['GPSInfo']['GPSLatitudeRef'] in CARDINAL
    assert output['GPSInfo']['GPSLongitudeRef'] in CARDINAL

    assert len(output['GPSInfo']['GPSLatitude']) == 3
    assert len(output['GPSInfo']['GPSLongitude']) == 3
    assert type(output['GPSInfo']['GPSAltitude']) == float

def test_extract_metadata_from_filepath():
    source_img = Image.open(TEST_IMG_FILEPATH)
    output = extract_metadata(source_img)
    assert extract_metadata_from_filepath(TEST_IMG_FILEPATH) == output