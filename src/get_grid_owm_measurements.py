import time
from datetime import datetime
from geopy.geocoders import Nominatim

from dbutl.functions.make_connection import make_connection
from dbutl.functions.insert_into_table import insert_into_table
from config import db_credentials, owm_measurements_logger as logger
from owm_api.functions import get_random_api_key, make_request_to_owm_api, generate_owm_grid,\
    get_average_parameters_values_from_last_24h


TABLE_NAME = "measurements_grid_owm"
TABLE_COLUMNS = ["date", "latitude", "longitude", "pm25", "pm10"]

current_date = datetime.now()
START_DT = int(current_date.strftime('%s')) - 24*3600
END_DT = current_date.strftime('%s')


def generate_url(lat, lon, start_dt, end_dt, api_key):
    return f"http://api.openweathermap.org/data/2.5/air_pollution/history" \
           f"?lat={lat}&lon={lon}&start={start_dt}&end={end_dt}&appid={api_key}"


if __name__ == "__main__":
    conn = make_connection(db_credentials)
    latitudes, longitudes = generate_owm_grid()

    geolocator = Nominatim(user_agent="geopy")

    data_to_insert = []
    attempts = 0
    foreign_locations = 0
    invalid_measurements = 0
    logger.info("Measurements acquiring started")
    for lat in latitudes:
        for lng in longitudes:
            attempts += 1
            time.sleep(.5)
            location = geolocator.reverse(f"{lat},{lng}")
            if location is None:
                foreign_locations += 1
                continue

            country = location.raw['address']['country']
            if country.lower() not in ['polska', 'poland']:
                foreign_locations += 1
                continue

            api_key = get_random_api_key()
            url = generate_url(lat, lng, START_DT, END_DT, api_key)
            measurements_resp = make_request_to_owm_api(url)

            if measurements_resp.ok:
                data_24h = measurements_resp.json()["list"]
                measurements_values = [{"PM25": item['components']['pm2_5'],
                                        "PM10": item['components']['pm10']} for item in data_24h]
                valid_measurements = measurements_values

                try:
                    avg_values_dict = get_average_parameters_values_from_last_24h(
                        valid_measurements, (lat, lng), logger)
                except Exception as e:
                    logger.error(f"Grid measurement for coordinates ({lat}, {lng})"
                                 f" not taken due to: {e}")
                    invalid_measurements += 1
                    continue

                one_row_dict = {"DATE": current_date.strftime('%Y-%m-%d'),
                                "LATITUDE": lat, "LONGITUDE": lng}
                for key, val in avg_values_dict.items():
                    one_row_dict[key] = val

                data_to_insert.append(one_row_dict)
            else:
                logger.error(
                    f"Response invalid for coordinates {(lat, lng)}, url: {url}. "
                    f"Response code: {measurements_resp.status_code}")

    logger.info(
        f"{len(data_to_insert)} measurements acquired out of {attempts} attempts for the"
        f" OWM grid, date {current_date}. {foreign_locations} locations are out of Poland. "
        f"Invalid measurements: {invalid_measurements}. Inserting starting.")

    attempts = 0
    succeeded_inserts = 0
    for measurement in data_to_insert:
        attempts += 1
        try:
            insert_into_table(TABLE_NAME, column_names=TABLE_COLUMNS,
                              values=list(measurement.values()), conn=conn)
            succeeded_inserts += 1
        except Exception as e:
            lat, lng = measurement['LATITUDE'], measurement['LONGITUDE']
            logger.error(
                f"Measurement from installation with coords {(lat, lng)} not inserted to"
                f" db due to: {e}")

    logger.info(f"Inserted {succeeded_inserts} out of {attempts} attempts")
    conn.close()
