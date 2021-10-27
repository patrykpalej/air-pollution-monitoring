import os
from dotenv import load_dotenv

load_dotenv()


# DB ENVIRONMENT VARIABLES
db_envionment_variables = ["DBNAME", "USER", "PASSWORD", "HOST", "PORT"]
db_credentials = dict.fromkeys(db_envionment_variables)
for variable in db_envionment_variables:
    db_credentials[variable] = os.getenv(variable)
