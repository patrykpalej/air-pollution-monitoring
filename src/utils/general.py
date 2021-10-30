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
