import logging

import requests
import numpy as np
from typing import Optional

from config import airly_api_keys
from utils.general import get_random_proxy_dict
from utils.geographic import transform_azimuth_to_xy, transform_xy_to_azimuth


def get_random_api_key():
    return np.random.choice(airly_api_keys)


def make_request_to_airly_api(url: str, api_key: str,
                              use_proxy: Optional[bool] = False) -> requests.Response:
    """
    Send a request to airly API and return a response

    Parameters
    ----------
    url : str
    api_key : str
    use_proxy : bool

    Returns
    -------
    response : JSON
    """
    headers = {"apikey": api_key, "Accept-Encoding": "gzip"}

    proxy_dict = None
    if use_proxy:
        proxy_dict = get_random_proxy_dict()

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict)
    except requests.exceptions.ProxyError:
        response = requests.get(url, headers=headers)
        print("Invalid proxy")
        print(proxy_dict)

    return response


def get_average_parameters_values_from_last_24h(values: list, coordinates: tuple,
                                                logger: logging.Logger):
    """
    Takes a list of measurements and returns a dictionary of average values for subsequent params
    Parameters
    ----------
    values : list[dict] - for each timestamp there is one dictionary of params such as pm2.5,
     pm10, pressure, temperature etc. measured
    coordinates : tuple of (lat, lng) needed for logging
    logger : logging.Logger

    Returns
    -------
    avg_values_dict : dict - average values of: pm2.5, pm10, pressure, humidity, temperature,
        wind speed, wind bearing
    """
    def calc_avg_value_of_param(param_name):
        return np.array([v[parameters_idxs[param_name]]["value"] for v in values]).mean()

    def ensure_all_timestamps_have_same_parameters_measured():
        first_measurement_set_of_params = [measure["name"] for measure in values[0]]
        for measurement in values:
            if [m["name"] for m in measurement] != first_measurement_set_of_params:
                return False
        return True

    _ALL_PARAMS_TO_AVG = ["PM25", "PM10", "PRESSURE", "HUMIDITY", "TEMPERATURE", "WIND_SPEED"]
    avg_values_dict = dict().fromkeys(_ALL_PARAMS_TO_AVG)

    if not ensure_all_timestamps_have_same_parameters_measured():
        logger.error(f"For these coords {coordinates} not all timestamps have the same parameters."
                     f" It may cause inaccuracies - aborting")
        raise Exception(f"Measured elements change from hour to hour for coords ({coordinates})")

    parameters_idxs = dict([(val, i) for i, val in enumerate([item["name"] for item in values[0]])])
    measured_params = list(parameters_idxs.keys())
    needed_measured_params = list(set(measured_params) & set(_ALL_PARAMS_TO_AVG))

    for param in needed_measured_params:
        avg_values_dict[param] = calc_avg_value_of_param(param)

    avg_values_dict["WIND_BEARING"] = None
    if "WIND_BEARING" in measured_params:
        wind_speed_arr = np.array([v[parameters_idxs["WIND_SPEED"]]["value"] for v in values])
        wind_bearing_arr = np.array([v[parameters_idxs["WIND_BEARING"]]["value"] for v in values])
        wind_bearing_xy_arr = np.array([transform_azimuth_to_xy(wb) for wb in wind_bearing_arr])

        weighted_avg_wb_xy = (np.average(wind_bearing_xy_arr[:, 0], weights=wind_speed_arr),
                              np.average(wind_bearing_xy_arr[:, 1], weights=wind_speed_arr))
        weighted_avg_wb_azimuth = transform_xy_to_azimuth(*weighted_avg_wb_xy)

        avg_values_dict["WIND_BEARING"] = weighted_avg_wb_azimuth

    return avg_values_dict
