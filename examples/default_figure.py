"""
Example of including a default figure to use with dash-chart-editor

Note that it's necessary to add the following to the default figure:

  - `xsrc` – Sets the source reference on dash-chart-editor for x.
  - `ysrc` – Sets the source reference on dash-chart-editor for y.

"""


import dash_chart_editor as dce
from dash import Dash, html
import plotly.express as px


app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

df = px.data.gapminder()


default_fig = px.scatter(
    df.query("year==2007"),
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    log_x=True,
    size_max=60,
    template="plotly_dark",
)

default_fig["data"][0]["xsrc"] = "gpdPercap"
default_fig["data"][0]["ysrc"] = "lifeExp"


app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo with the Plotly Gapminder dataset"),
        dce.DashChartEditor(
            dataSources=df.to_dict("list"),
            loadFigure=default_fig,
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
