import pytest
from PIL import Image
from datetime import datetime as dt

from extract_metadata import extract_metadata, extract_metadata_from_filepath, coordinates_to_decdegrees, process_GPS_data

TEST_IMG_FILEPATH = 'IMG_1379.JPG'
CARDINAL = ['N', 'E', 'S', 'W']
LAT1 = [50.0, 43.0, 18.43, 'S']
LON1 = [3.0, 32.0, 0.21, 'W']
LAT2 = [46.0, 12.0, 23.04, 'N']
LON2 = [27.0, 39.0, 0.5616, 'E']

def test_extract_metadata():
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

def test_coordinates_to_decdegrees():
    assert coordinates_to_decdegrees(LAT1, LON1) == (-50.721786111111115, -3.5333916666666667)
    assert coordinates_to_decdegrees(LAT2, LON2) == (46.2064, 27.650156)

def test_process_GPS_data():
    source_img = Image.open(TEST_IMG_FILEPATH)
    assert process_GPS_data(source_img) == (50.721786111111115, -3.5333916666666667)
