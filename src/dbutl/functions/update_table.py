import os
import json
from typing import Union, Optional

from config import db_credentials
from config import script_logger as logger
from dbutl.functions.make_connection import make_connection


def generate_update_query(table_name: str, columns: list, values: list, where: Union[list, None]):
    values = [value if value not in [None, "None", "'None'"] else "NULL" for value in values]

    update_query = (f"UPDATE {table_name} SET "
                    f"{','.join([col + '=' + val for col, val in zip(columns, values)])};")
    if where is not None:
        update_query = (update_query[:-1] + " WHERE " + " AND ".join(
            [f"{condition[0]} = {condition[1]}" for condition in where]) + ";")

    return update_query


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


def update_table(table_name: str, column_names: Union[list, tuple], values: Union[list, tuple],
                 where: Optional[list] = None, conn=None):
    """
    Parameters
    ----------
    table_name : str
    column_names : list - list of columns (strings) to be updates
    values : list - list of values to be updated
    where : tuple - optional WHERE condition in a format [( <column_name>, <value_in_that_column> )]
    conn : psycopg2.extensions.connection - connection to db
    """
    values_with_apostrophes = add_apostrophes_to_values(values, table_name, column_names)
    update_query = generate_update_query(table_name, column_names, values_with_apostrophes, where)

    should_conn_be_closed = False
    if conn is None:
        conn = make_connection(db_credentials)
        should_conn_be_closed = True

    cursor = conn.cursor()

    try:
        cursor.execute(update_query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Table '{table_name}' updating failed. Error message: {e}")

    cursor.close()
    if should_conn_be_closed:
        conn.close()
