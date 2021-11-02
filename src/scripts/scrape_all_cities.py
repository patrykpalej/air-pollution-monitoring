import re
import requests
from functools import partial
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

from config import db_credentials
from config import script_logger as logger
from dbutl.functions.make_connection import make_connection
from dbutl.functions.insert_into_table import insert_into_table


geolocator = Nominatim(user_agent="geopy")
geocode = partial(geolocator.geocode, language="pl")

url = "https://www.polskawliczbach.pl/Miasta"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table_rows = soup.find("tbody").find_all("tr")

cities = list()

if __name__ == "__main__":
    logger.info("Scraping of cities started")
    for row in table_rows:
        city_name = row.find_all("td")[1].text
        latitude = geocode(city_name.lower()).latitude
        longitude = geocode(city_name.lower()).longitude
        population = int(re.sub(r"\s+", "", row.find_all("td")[4].text))
        area = None if row.find_all("td")[5].text == "-" else float(
            row.find_all("td")[5].text.replace(",", ".").replace(" km²", ""))
        voivodeship = row.find_all("td")[3].text

        single_city_dict = {"city_name": city_name, "latitude": latitude, "longitude": longitude,
                            "population": population, "area": area, "voivodeship": voivodeship}
        cities.append(single_city_dict)

    logger.info("All cities scraped. Inserting to db starting")

    conn = make_connection(db_credentials)
    for city in cities:
        try:
            insert_into_table(table_name="cities", column_names=list(city.keys()),
                              values=list(city.values()), conn=conn)
        except Exception as e:
            logger.error(f"City '{city['city_name']}' insertion failed\n{e}\n")

    conn.close()

    logger.info("All cities inserted to db")
