import requests
import numpy as np
from typing import Optional

from config import airly_api_keys
from utils.general import get_random_proxy_dict


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
    headers = {"apikey": api_key}

    proxy_dict = None
    if use_proxy:
        proxy_dict = get_random_proxy_dict()

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict)
    except requests.exceptions.ProxyError:
        response = requests.get(url, headers=headers)
        print("Invalid proxy")
        print(proxy_dict)
        # TODO log invalid proxy including timestamp
        # TODO why proxies dont work in Pycharm but they do in JN?

    return response
