from dash import dcc
from dash import html

from frontend.tab_1 import tab_1
from frontend.tab_2 import tab_2
from frontend.tab_3 import tab_3


def frontend():
    layout_ = html.Div([
        dcc.Tabs(id="app_tabs", value="tab1",
                 children=[dcc.Tab(children=tab_1(),
                                   id="tab_1", value="tab1",
                                   label="Zanieczyszczenia powietrza - mapa"),
                           dcc.Tab(children=tab_2(), id="tab_2", value="tab2",
                                   label="Zanieczyszczenia powietrza - porównanie miast"),
                           dcc.Tab(children=tab_3(), id="tab_3", value="tab3",
                                   label="Pogoda")],
                 style={})
    ])

    return layout_
