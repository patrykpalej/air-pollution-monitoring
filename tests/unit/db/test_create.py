from dbutl.functions.create_single_table import return_not_null
from dbutl.functions.create_single_table import return_unique
from dbutl.functions.create_single_table import create_single_table


def test_return_not_null():
    assert return_not_null(1) == "NOT NULL"
    assert return_not_null(0) == ""


def test_return_unique():
    assert return_unique(1) == "UNIQUE"
    assert return_unique(0) == ""


def test_create_single_table():
    test_table_config = {
        "name": "test_table",
        "columns": [
            {"name": "text_column", "type": "text"},
            {"name": "date_column", "type": "date"},
            {"name": "numeric_column", "type": "NUMERIC(6, 3)"},
            {"name": "numeric_column1", "type": "NUMERIC"},
            {"name": "varchar_column", "type": "VARCHAR(10)"}
        ]
    }

    create_single_table(test_table_config, commit=False)
