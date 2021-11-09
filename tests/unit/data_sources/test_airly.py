import json
import numpy as np

from config import airly_grid_logger as logger
from airly_api.functions import get_average_parameters_values_from_last_24h
from utils.geographic import transform_xy_to_azimuth, transform_azimuth_to_xy, calculate_distance


with open("tests/mocks/airly_data.json", "r") as f:
    VALUES = json.load(f)


def test_get_average_parameters_values_from_last_24h():
    avg_values_dict = get_average_parameters_values_from_last_24h(VALUES, (0, 0), logger)

    assert list(avg_values_dict.keys()) == ["PM25", "PM10", "PRESSURE", "HUMIDITY",
                                            "TEMPERATURE", "WIND_SPEED", "WIND_BEARING"]
    assert avg_values_dict["PM25"] == 19.5
    assert avg_values_dict["PM10"] == 29.5
    assert avg_values_dict["PRESSURE"] == 1009.5
    assert avg_values_dict["HUMIDITY"] == 89.5
    assert avg_values_dict["TEMPERATURE"] == 15.5
    assert avg_values_dict["WIND_SPEED"] == 10.5
    assert avg_values_dict["WIND_BEARING"] == 313.081344077875


def test_transform_azimuth_to_xy():
    azimuth_data = [0, 30, 60, 120, 180, 300, 360, 400]
    xy_data = [(0.0, 1.0),
               (0.49999999999999994, 0.8660254037844387),
               (0.8660254037844386, 0.5000000000000001),
               (0.8660254037844387, -0.4999999999999998),
               (1.2246467991473532e-16, -1.0),
               (-0.8660254037844386, 0.5000000000000001),
               (-2.4492935982947064e-16, 1.0),
               (0.6427876096865391, 0.7660444431189781)]

    for azimuth, xy in zip(azimuth_data, xy_data):
        result = transform_azimuth_to_xy(azimuth)

        assert xy[0] + 0.01 >= result[0] >= xy[0] - 0.01
        assert xy[1] + 0.01 >= result[1] >= xy[1] - 0.01


def test_transform_xy_to_azimuth():
    azimuth_data = [0, 30, 60, 120, 180, 300, 0, 40]
    xy_data = [(0.0, 1.0),
               (0.49999999999999994, 0.8660254037844387),
               (0.8660254037844386, 0.5000000000000001),
               (0.8660254037844387, -0.4999999999999998),
               (1.2246467991473532e-16, -1.0),
               (-0.8660254037844386, 0.5000000000000001),
               (-2.4492935982947064e-16, 1.0),
               (0.6427876096865391, 0.7660444431189781)]

    for azimuth, xy in zip(azimuth_data, xy_data):
        result = transform_xy_to_azimuth(xy[0], xy[1])

        assert azimuth + 0.01 >= result >= azimuth - 0.01
        assert azimuth + 0.01 >= result >= azimuth - 0.01


def test_calculate_distance():
    coordinates = [[(50, 20), (40, 25)], [(10, 20), (-25, 20)], [(0, 0), (-20, -30)]]
    distances = [1178.4800116714475, 3871.9090023803965, 3947.8079810936865]

    for coord, dist in zip(coordinates, distances):
        distance_calculated = calculate_distance(coord[0], coord[1])
        assert np.abs(dist-distance_calculated) < 0.01
