import os
import json
from typing import Union

from config import db_credentials
from dbutl.functions.make_connection import make_connection


def generate_insert_query(table_name: str, columns: list, values: list):
    return f"INSERT INTO {table_name}({','.join(columns)}) VALUES({','.join(values)});"


def value_does_need_apostrophes(postgresql_type):
    if (postgresql_type.lower() == "text"
            or "varchar" in postgresql_type.lower()
            or "date" in postgresql_type.lower()):
        return True

    return False


def add_apostrophes_to_values(values: list, table_name: str, column_names: list) -> list:
    """
    Checks whether values in specific columns need apostrophe before passing them to the query
    generator

    Parameters
    ----------
    values : list - values which are to be inserted
    table_name : str - table to which data is to be inserted
    column_names : list - columns to which data is to be inserted

    Returns
    -------
    values_with_apostrophes : list - values with added apostrophes if needed
    """
    table_config_path = f"{os.getenv('PYTHONPATH').split(':')[0]}/config/tables/{table_name}.json"
    with open(table_config_path, "r") as f:
        table_config = json.load(f)

    values_with_apostrophes = []
    for col, val in zip(column_names, values):
        column_position = None
        for i, item in enumerate(table_config["columns"]):
            if item["name"] == col:
                column_position = i
                break

        if column_position is None:
            raise Exception(f"Column '{col}' not present in table '{table_name}'")

        if value_does_need_apostrophes(table_config["columns"][column_position]["type"]):
            values_with_apostrophes.append(f"'{val}'")
        else:
            values_with_apostrophes.append(f"{val}")

    return values_with_apostrophes


def insert_into_table(table_name: str, column_names: list, values: Union[list, tuple]):
    """
    Parameters
    ----------
    table_name : str
    column_names : list - list of columns (strings) to be inserted to
    values : list - list of values to be inserted
    """
    values_with_apostrophes = add_apostrophes_to_values(values, table_name, column_names)
    insert_query = generate_insert_query(table_name, column_names, values_with_apostrophes)

    conn = make_connection(db_credentials)
    cursor = conn.cursor()
    cursor.execute(insert_query)
    conn.commit()
