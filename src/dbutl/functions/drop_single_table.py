from config import db_credentials
from dbutl.functions.make_connection import make_connection


def generate_drop_query(table_name: str) -> str:
    return f"DROP TABLE {table_name};"


def drop_single_table(table_name: str):
    """
    Parameters
    ----------
    table_name : str
    """
    drop_query = generate_drop_query(table_name)

    conn = make_connection(db_credentials)
    cursor = conn.cursor()
    cursor.execute(drop_query)
    conn.commit()
