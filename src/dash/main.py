import dash

from layout import frontend


app = dash.Dash(__name__)
app.layout = frontend()


if __name__ == '__main__':
    app.run_server(debug=True, port=1234)
