from functions.drop_single_table import drop_single_table


table_names = ["measurements_cities_airly", "measurements_coordinates_airly", "cities"]

for table in table_names:
    try:
        drop_single_table(table)
        print(f"Table {table} dropped successfully")
    except Exception as e:
        print(f"Error in dropping table {table}\n{e}\n")
