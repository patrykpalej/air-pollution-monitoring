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

    if all_installations_nearby_response.ok:
        all_installations_nearby = all_installations_nearby_response.json()

        column_names = ["location_id", "latitude", "longitude", "elevation", "country", "city"]
        locations_list = []
        for item in all_installations_nearby:
            location_id = item["locationId"]
            latitude = item["location"]["latitude"]
            longitude = item["location"]["longitude"]
            elevation = item["elevation"]
            country = item["address"]["country"]
            city = item["address"]["city"]

            location_dict = dict()
            for feature in column_names:
                location_dict[feature] = eval(feature)

            locations_list.append(location_dict)

        for location in locations_list:
            insert_into_table(table_name="locations_airly", column_names=column_names,
                              values=list(location.values()))

    else:
        raise Exception("Requesting airly locations didn't succeed")
