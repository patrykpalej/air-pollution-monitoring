import json
import pandas as pd

from config import db_credentials
from config import airly_grid_logger as logger
from utils.geographic import find_optimal_grid_points
from dbutl.functions.make_connection import make_connection
from dbutl.functions.insert_into_table import insert_into_table
from airly_api.functions import get_random_api_key, make_request_to_airly_api


CENTRAL_POINT_LAT = 52.028
CENTRAL_POINT_LNG = 19.532
MAX_RESULTS = 5000
MAX_DISTANCE = 500

with open("config/invalid_installations_airly.json", "r") as f:
    INVALID_INSTALLATIONS = list(set(json.load(f)["ids"]))

url = (f"https://airapi.airly.eu/v2/installations/nearest?lat={CENTRAL_POINT_LAT}"
       f"&lng={CENTRAL_POINT_LNG}&maxResults={MAX_RESULTS}&maxDistanceKM={MAX_DISTANCE}")
api_key = get_random_api_key()

if __name__ == "__main__":
    all_installations_nearby_response = make_request_to_airly_api(url=url, api_key=api_key)
    logger.info("Request to airly API made")
    logger.debug(f"Request URL ending: {url.split('.eu')[1]} | API key: {api_key}")

    if all_installations_nearby_response.ok:
        logger.info("HTTP response is OK")
        all_installations_nearby = all_installations_nearby_response.json()

        if len(all_installations_nearby) == 0:
            logger.warning("List of installations received from API doesn't contain any items")
        else:
            logger.debug(f"List of {len(all_installations_nearby)} records received from API")

        grid_column_names = ["installation_id", "location_id", "city_name", "latitude", "longitude"]
        all_installations_list = []
        for item in all_installations_nearby:
            installation_id = item["id"]
            location_id = item["locationId"]
            city_name = str(item["address"]["city"]).replace("Warsaw", "Warszawa")
            latitude = item["location"].get("latitude")
            longitude = item["location"].get("longitude")
            country = item["address"].get("country")

            installation_dict = dict()
            for feature in grid_column_names:
                installation_dict[feature] = eval(feature)

            if country == "Poland" and installation_id not in INVALID_INSTALLATIONS:
                all_installations_list.append(installation_dict)

        logger.info(f"{len(all_installations_list)} Polish airly installations scraped,"
                    f" grid calculating starting")

        cities_df_select_query = "SELECT * FROM cities"
        conn = make_connection(db_credentials)
        cities_df = pd.read_sql(cities_df_select_query, conn)
        if len(cities_df) == 0:
            logger.error("Cities table read from db is empty")

        grid = find_optimal_grid_points(all_installations_list, cities_df)

        logger.info(f"{len(grid)} grid points set, starting inserting them to db")

        attempts = 0
        succeeded_inserts = 0
        for grid_point in grid:
            attempts += 1
            try:
                insert_into_table(table_name="grid_airly", column_names=grid_column_names,
                                  values=list(grid_point.values()), conn=conn)
                succeeded_inserts += 1
            except Exception as e:
                logger.error(f"Error in inserting data to 'grid_airly' table: {e}")

        logger.info(f"{succeeded_inserts} grid points out of {attempts} attempts inserted to db")
        conn.close()

    else:
        logger.critical("HTTP response is not OK when scraping airly installations")
        raise Exception("Requesting airly installations didn't succeed")

logger.info("Scraping airly installations finished")
