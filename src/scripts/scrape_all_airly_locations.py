from config import script_logger as logger
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

        column_names = ["location_id", "latitude", "longitude", "elevation", "country", "city"]
        locations_list = []
        for item in all_installations_nearby:
            location_id = item.get("locationId")
            latitude = item["location"].get("latitude")
            longitude = item["location"].get("longitude")
            elevation = item.get("elevation")
            country = item["address"].get("country")
            city = item["address"].get("city")

            location_dict = dict()
            for feature in column_names:
                location_dict[feature] = eval(feature)

            if None in location_dict.values():
                logger.error(f"At least one of location features is None."
                             f" Location id: {location_id}")

            locations_list.append(location_dict)

        for location in locations_list:
            try:
                insert_into_table(table_name="locations_airly", column_names=column_names,
                                  values=list(location.values()))
            except Exception as e:
                logger.error(f"Error in inserting location with id={location['location_id']}: {e}")

    else:
        logger.critical("HTTP response is not OK when scraping airly locations")
        raise Exception("Requesting airly locations didn't succeed")
