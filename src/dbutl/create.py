import json

from functions.create_single_table import create_single_table


table_names = ["measurements_cities_airly", "measurements_coordinates_airly", "cities"]

for table in table_names:
    with open(f"config/tables/{table}.json", "r") as f:
        table_config = json.load(f)

    try:
        create_single_table(table_config)
        print(f"Table {table} created successfully")
    except Exception as e:
        print(f"Error in creating table {table}\n{e}\n")
