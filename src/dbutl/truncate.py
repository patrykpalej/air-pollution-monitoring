import sys

from config import db_credentials
from dbutl.functions.make_connection import make_connection
from functions.truncate_single_table import truncate_single_table


if len(sys.argv) > 1:
    table_names = sys.argv[1:]
else:
    table_names = ["measurements_grid_airly"]

conn = make_connection(db_credentials)
for table in table_names:
    try:
        truncate_single_table(table, conn=conn)
        print(f"Table '{table}' truncated successfully")
    except Exception as e:
        print(f"Error in truncating table {table}\n{e}\n")

conn.close()
