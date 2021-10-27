from functions.delete_single_table import delete_single_table


table_names = ["measurements_cities_airly", "measurements_coordinates_airly", "cities"]

for table in table_names:
    try:
        delete_single_table(table)
        print(f"Table {table} deleted successfully")
    except Exception as e:
        print(f"Error in deleting table {table}\n{e}\n")
