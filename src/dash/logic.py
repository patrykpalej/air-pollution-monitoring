import plotly.express as px


def create_plot(df):
    fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='pm25', animation_frame="date",
                            radius=40, center={'lat': 52, 'lon': 19.2}, zoom=5.1,
                            mapbox_style="open-street-map", range_color=[0, max(df['pm25'])],
                            color_continuous_scale='jet')

    fig.update_layout(width=740, height=740)

    return fig

