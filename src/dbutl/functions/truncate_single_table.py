from config import db_credentials
from dbutl.functions.make_connection import make_connection


def generate_truncate_query(table_name: str) -> str:
    return f"TRUNCATE TABLE {table_name};"


def truncate_single_table(table_name: str):
    """
    Parameters
    ----------
    table_name : str
    """
    delete_query = generate_truncate_query(table_name)

    conn = make_connection(db_credentials)
    cursor = conn.cursor()
    cursor.execute(delete_query)
    conn.commit()

    conn.close()
    cursor.close()
