from dbutl.functions.create_single_table import create_single_table
from dbutl.functions.insert_into_table import insert_into_table
from dbutl.functions.delete_single_table import delete_single_table
from dbutl.functions.drop_single_table import drop_single_table


def test_whole_db_flow():
    # CREATE
    test_table_config = {
        "name": "test_table_name",
        "columns": [
            {"name": "text_column", "type": "text"},
            {"name": "date_column", "type": "date"},
            {"name": "numeric_column", "type": "NUMERIC(6, 3)"},
            {"name": "numeric_column1", "type": "NUMERIC"},
            {"name": "varchar_column", "type": "VARCHAR(10)"}
        ]
    }

    create_single_table(test_table_config)

    # INSERT
    mockup_data = [("Lorem ipsum dolor sit amet, consectetur adipis",
                   "2018-04-23", 24.254, 1325.7, "Test text"),
                   ("Another long text", "2019-12-14", 1.32, 65, "varchar 10")]

    for data_row in mockup_data:
        insert_into_table(table_name=test_table_config["name"],
                          column_names=[column["name"] for column in test_table_config["columns"]],
                          values=data_row)

    # SELECT
    # TODO test select and update queries

    # DELETE
    delete_single_table(test_table_config["name"])

    # DROP
    drop_single_table(test_table_config["name"])
