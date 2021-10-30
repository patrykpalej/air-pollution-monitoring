import os
import json
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
