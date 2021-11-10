from typing import Optional
from config import db_credentials
from dbutl.functions.make_connection import make_connection


def return_not_null(is_not_null: int) -> str:
    return "NOT NULL" if is_not_null else ""


def return_unique(is_unique: int) -> str:
    return "UNIQUE" if is_unique else ""


def generate_create_query(table_config: dict) -> str:
    """
    Parameters
    ----------
    table_config: JSON - configuration JSON of a table

    Returns
    -------
    create_query : str - create query of the table
    """
    create_query = f"CREATE TABLE {table_config['name']} ("

    single_columns_definitions = []
    for col in table_config["columns"]:
        single_column_definition = col["name"] + " " + col["type"] + " " + return_not_null(
            col.get("not_null", 0)) + " " + return_unique(col.get("unique", 0))
        single_columns_definitions.append(single_column_definition)

    columns_definition = ','.join(single_columns_definitions)

    if "unique_set" in table_config:
        columns_definition += ", UNIQUE("
        unique_columns = []
        for item in table_config["unique_set"]:
            unique_columns.append(item)
        columns_definition += ", ".join(unique_columns) + ")"

    create_query += columns_definition + ");"

    return create_query


def create_single_table(table_config: dict, commit: Optional[bool] = True, conn=None):
    """
    Parameters
    ----------
    table_config : JSON - configuration JSON of a table
    commit : bool - whether or not to commit changes
    conn : psycopg2.extensions.connection - connection to db
    """
    create_query = generate_create_query(table_config)

    should_conn_be_closed = False
    if conn is None:
        conn = make_connection(db_credentials)
        should_conn_be_closed = True

    cursor = conn.cursor()
    try:
        cursor.execute(create_query)
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Creating table {table_config['name']} failed due to: {e}")

    cursor.close()
    if should_conn_be_closed:
        conn.close()

