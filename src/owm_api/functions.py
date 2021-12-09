import logging
import requests
import numpy as np

from config import owm_api_keys, latitude_lims, longitude_lims


def get_random_api_key():
    return np.random.choice(owm_api_keys)


def make_request_to_owm_api(url: str) -> requests.Response:
    response = requests.get(url)
    return response


def generate_owm_grid(density: int = 30) -> tuple:
    return (np.linspace(latitude_lims[0], latitude_lims[1], density),
            np.linspace(longitude_lims[0], longitude_lims[1], density))


def get_average_parameters_values_from_last_24h(values: list, coordinates: tuple,
                                                logger: logging.Logger):
    """
    Takes a list of measurements and returns a dictionary of average values for subsequent params
    Parameters
    ----------
    values : list[dict] - for each timestamp there is one dictionary of params (pm2.5, pm10)
    coordinates : tuple of (lat, lng) needed for logging
    logger : logging.Logger

    Returns
    -------
    avg_values_dict : dict - average values of pm2.5 and pm10
    """
    try:
        avg_pm25 = np.array([item["PM25"] for item in values]).mean()
        avg_pm10 = np.array([item["PM10"] for item in values]).mean()

        avg_values_dict = {"PM25": avg_pm25, "PM10": avg_pm10}
        return avg_values_dict

    except Exception as e:
        logger.error(f"For coordinates ({coordinates} average values couldn't be calculated"
                     f" because of: {e})")
        raise Exception("Average values couldn't be calculated'")
