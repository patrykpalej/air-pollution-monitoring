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
api_keys_json_path = f"{os.getenv('PYTHONPATH').split(':')[0]}/config/api_keys.json"
with open(api_keys_json_path, "r") as f:
    api_keys = json.load(f)

airly_api_keys = api_keys["airly"]
owm_api_keys = api_keys["owm"]


# PROXIES
proxies_json_path = f"{os.getenv('PYTHONPATH').split(':')[0]}/config/proxies.json"
with open(proxies_json_path, "r") as f:
    proxies = json.load(f)


# GEOGRAPHY
latitude_lims = [49, 55]
longitude_lims = [14, 24.1]


# LOGGING
loggers = ["airly_grid_logger", "airly_measurements_logger", "scraping_cities_logger",
           "owm_measurements_logger"]
loggers_dict = dict().fromkeys(loggers)

for logger in loggers:
    loggers_dict[logger] = logging.getLogger(logger)
    loggers_dict[logger].setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s -- %(message)s')
    file_path = f"{os.getenv('PYTHONPATH').split(':')[0]}/log/{logger.replace('_logger', '')}.log"

    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    loggers_dict[logger].addHandler(file_handler)
    loggers_dict[logger].addHandler(stream_handler)


for logger in loggers:
    exec(f"{logger} = loggers_dict[logger]")
