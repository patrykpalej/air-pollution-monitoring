from dash import dcc
from dash import html

from datetime import datetime


def tab_1():
    layout = html.Div([

        html.Div(["Rodzaj zanieczyszczenia",
                  dcc.Dropdown(id='1_choose_pollutant', placeholder="Rodzaj zanieczyszczenia",
                               options=[
                                   {"label": "PM 2.5", "value": 'pm25'},
                                   {"label": "PM 10", "value": 'pm10'},
                                   {"label": "Średnia", "value": 'avg'}])],
                 style={"width": "10vw", "top": "10vh", "left": "2vw", "position": "absolute",
                        "display": "grid"}),

        html.Div(["Źródło danych",
                  dcc.Checklist(id='1_choose_data_source', options=[
                      {"label": "Airly", "value": 'airly'},
                      {"label": "OpenWeatherMap", "value": 'owm'},
                      {"label": "GIOS", "value": 'gios'}], labelStyle={'display': 'block'})],
                 style={"width": "10vw", "top": "10vh", "left": "20vw", "position": "absolute",
                        "display": "grid"}),

        html.Div([
            dcc.DatePickerRange(
                id="1_date_picker", display_format="DD-MM-YYYY",
                min_date_allowed=datetime(2020, 1, 1), max_date_allowed=datetime.now(),
            )], style={"top": "10vh", "left": "40vw", "position": "absolute"}),

        dcc.Graph(id="1_graph_1", figure={},
                  style={"width": "40vw", "height": "60vh", "position": "absolute",
                         "left": "5vw", "top": "30vh"}),

        dcc.Graph(id="1_graph_2", figure={},
                  style={"width": "40vw", "height": "60vh", "position": "absolute",
                         "left": "50vw", "top": "30vh"})

    ])

    return layout
