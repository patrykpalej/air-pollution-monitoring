from config import db_credentials
from dbutl.functions.make_connection import make_connection


def generate_truncate_query(table_name: str) -> str:
    return f"TRUNCATE TABLE {table_name};"


def truncate_single_table(table_name: str, conn=None):
    """
    Parameters
    ----------
    table_name : str
    conn : psycopg2.extensions.connection - connection to db
    """
    truncate_query = generate_truncate_query(table_name)

    should_conn_be_closed = False
    if conn is None:
        conn = make_connection(db_credentials)
        should_conn_be_closed = True

    cursor = conn.cursor()
    try:
        cursor.execute(truncate_query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Deleting table {table_name} failed due to: {e}")

    cursor.close()
    if should_conn_be_closed:
        conn.close()
