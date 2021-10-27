import psycopg2

from config import db_credentials


conn = psycopg2.connect(**db_credentials)
print(conn)
