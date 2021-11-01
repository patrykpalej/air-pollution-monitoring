import pandas as pd

from config import db_credentials
from config import script_logger as logger
from utils.geographic import find_optimal_grid_points
from dbutl.functions.make_connection import make_connection
from dbutl.functions.insert_into_table import insert_into_table
from airly_api.functions import get_random_api_key, make_request_to_airly_api


CENTRAL_POINT_LAT = 52.028
CENTRAL_POINT_LNG = 19.532
MAX_RESULTS = 5000
MAX_DISTANCE = 500

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

        grid_column_names = ["latitude", "longitude"]
        locations_list = []
        for item in all_installations_nearby:
            latitude = item["location"].get("latitude")
            longitude = item["location"].get("longitude")
            country = item["address"].get("country")

            location_dict = dict()
            for feature in grid_column_names:
                location_dict[feature] = eval(feature)

            if country == "Poland":
                locations_list.append(location_dict)

        logger.info("All airly locations scraped, grid calculating starting")

        locations_latitudes = [item["latitude"] for item in locations_list]
        locations_longitudes = [item["longitude"] for item in locations_list]

        cities_df_select_query = "SELECT * FROM cities"
        cities_df = pd.read_sql(cities_df_select_query, make_connection(db_credentials))

        grid = find_optimal_grid_points(locations_latitudes, locations_longitudes, cities_df)

        logger.info("Grid points set, starting inserting them to db")

        for grid_point in grid:
            try:
                insert_into_table(table_name="grid_airly", column_names=["latitude", "longitude"],
                                  values=grid_point)
            except Exception as e:
                logger.error(f"Error in inserting data to 'grid_airly' table: {e}")

    else:
        logger.critical("HTTP response is not OK when scraping airly locations")
        raise Exception("Requesting airly locations didn't succeed")

logger.info("Scraping airly locations finished")
