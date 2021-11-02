import sys
import json

from config import db_credentials
from dbutl.functions.make_connection import make_connection
from functions.create_single_table import create_single_table


if len(sys.argv) > 1:
    table_names = sys.argv[1:]
else:
    table_names = ["measurements_cities_airly", "measurements_coordinates_airly"]


conn = make_connection(db_credentials)
for table in table_names:
    try:
        with open(f"config/tables/{table}.json", "r") as f:
            table_config = json.load(f)
    except FileNotFoundError:
        print(f"Config file of table '{table}' not found")
        continue

    try:
        create_single_table(table_config, conn=conn)
        print(f"Table '{table}' created successfully")
    except Exception as e:
        print(f"Error in creating table {table}\n{e}\n")

conn.close()
