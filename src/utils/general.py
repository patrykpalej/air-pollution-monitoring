import numpy as np
from config import proxies


def get_random_proxy_dict() -> dict:
    """
    Returns dict with random proxy settings to be used in a request
    """
    random_proxy = np.random.choice(proxies)
    proxy_dict = {
        "http": f"http://{random_proxy}",
        "https": f"https://{random_proxy}"
    }

    return proxy_dict


def sort_dict(dict_: dict, by_value: bool = True) -> dict:
    """
    Returns dict sorted by values or keys
    """
    by_value = int(by_value)

    return {k: v for k, v in sorted(dict_.items(), key=lambda item: item[by_value])}
