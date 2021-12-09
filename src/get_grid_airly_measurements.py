import pandas as pd
from datetime import datetime

from dbutl.functions.make_connection import make_connection
from dbutl.functions.insert_into_table import insert_into_table
from config import db_credentials, airly_measurements_logger as logger
from airly_api.functions import get_average_parameters_values_from_last_24h
from airly_api.functions import get_random_api_key, make_request_to_airly_api


BASE_URL = ("https://airapi.airly.eu/v2/measurements/installation?includeWind=true"
            "&installationId=<INST_ID>")

TABLE_NAME = "measurements_grid_airly"
TABLE_COLUMNS = ["date", "latitude", "longitude", "installation_id", "pm25", "pm10", "pressure",
                 "humidity", "temperature", "wind_speed", "wind_bearing"]

if __name__ == "__main__":
    conn = make_connection(db_credentials)
    grid_airly_df = pd.read_sql("SELECT * FROM grid_airly", conn)
    latitudes = list(grid_airly_df["latitude"])
    longitudes = list(grid_airly_df["longitude"])
    installations = list(grid_airly_df["installation_id"])

    current_date = datetime.strftime(datetime.now(), '%Y-%m-%d')

    data_to_insert = []
    attempts = 0
    invalid_installations = []
    logger.info("Measurements acquiring started")
    for lat, lng, inst_id in zip(latitudes, longitudes, installations):
        attempts += 1
        url = BASE_URL.replace("<INST_ID>", str(inst_id))
        api_key = get_random_api_key()
        measurements_resp = make_request_to_airly_api(url=url, api_key=api_key)

        if measurements_resp.ok:
            data_24h = measurements_resp.json()["history"]
            measurement_values = [item["values"] for item in data_24h]
            valid_measurements = [item for item in measurement_values if item]

            if len(valid_measurements) < 18:
                logger.error(f"Less than 18 hours measured ({len(valid_measurements)}),"
                             f" omitting the measurement from installation #{inst_id} {(lat, lng)}")
                invalid_installations.append(inst_id)
                continue

            if len(valid_measurements) < 24:
                logger.warning(f"For installation #{inst_id} {(lat, lng)} historical values are"
                               f" not for 24 hours but {len(valid_measurements)}."
                               f" Still considered as valid")

            try:
                avg_values_dict = get_average_parameters_values_from_last_24h(
                    valid_measurements, (lat, lng), logger)
            except Exception as e:
                logger.error(f"Grid measurement for installation #{inst_id} ({lat}, {lng})"
                             f" not taken due to: {e}")
                invalid_installations.append(inst_id)
                continue

            one_row_dict = {"DATE": current_date, "LATITUDE": lat, "LONGITUDE": lng,
                            "INSTALLATION_ID": inst_id}
            for key, val in avg_values_dict.items():
                one_row_dict[key] = val

            data_to_insert.append(one_row_dict)
        else:
            logger.error(f"Response invalid for installation #{inst_id} {(lat, lng)}, url: {url}. "
                         f"Response code: {measurements_resp.status_code}")

    logger.info(f"{len(data_to_insert)} measurements acquired out of {attempts} attempts for the"
                f" airly grid, date {current_date}. Inserting starting.")

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
            logger.error(f"Measurement from installation with coords {(lat, lng)} not inserted to"
                         f" db due to: {e}")
            invalid_installations.append(measurement['INSTALLATION_ID'])

    logger.info(f"Inserted {succeeded_inserts} out of {attempts} attempts")
    logger.warning(f"{len(invalid_installations)} invalid installations,"
                   f" ids: {invalid_installations}")
    conn.close()
