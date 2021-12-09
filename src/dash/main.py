import dash
import pandas as pd
from dash.dependencies import Input, Output

from layout import frontend
from logic import create_plot

from config import db_credentials
from dbutl.functions.make_connection import make_connection


app = dash.Dash(__name__)
app.layout = frontend()


@app.callback(
     [Output('1_graph_1', 'figure')],
     [Input('1_choose_pollutant', 'value')]
)
def tab_1_create_left_plot(pollutant_dropdown):

    conn = make_connection(db_credentials)
    select_query = "SELECT * FROM measurements_grid_owm ORDER BY date"
    df = pd.read_sql(select_query, conn)
    df["date"] = df["date"].astype("str")

    plot = create_plot(df)
    return plot,


if __name__ == '__main__':
    app.run_server(debug=True, port=1234, host='0.0.0.0')
