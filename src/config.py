import os
import json
import logging
from dotenv import load_dotenv


load_dotenv()


# DB ENVIRONMENT VARIABLES
db_environment_variables = ["DBNAME", "DBUSER", "PASSWORD", "HOST", "PORT"]
envvar_dictkeys_dict = {"DBNAME": "dbname", "DBUSER": "user", "PASSWORD": "password",
                        "HOST": "host", "PORT": "port"}
db_credentials = dict()
for variable in db_environment_variables:
    db_credentials[envvar_dictkeys_dict[variable]] = os.getenv(variable)


# API KEYS
api_keys_json_path = "config/api_keys.json"
with open(api_keys_json_path, "r") as f:
    api_keys = json.load(f)

airly_api_keys = api_keys["airly"]
owm_api_keys = api_keys["owm"]


# PROXIES
proxies_json_path = "config/proxies.json"
with open(proxies_json_path, "r") as f:
    proxies = json.load(f)


# LOGGING
script_logger = logging.getLogger("script_logger")
script_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s - %(message)s')

file_handler = logging.FileHandler('log/scripts.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

script_logger.addHandler(file_handler)
script_logger.addHandler(stream_handler)

# ---
scraper_logger = logging.getLogger("script_logger")
scraper_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s - %(message)s')

file_handler = logging.FileHandler('log/scrapers.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

scraper_logger.addHandler(file_handler)
scraper_logger.addHandler(stream_handler)