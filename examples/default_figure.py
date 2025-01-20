"""
Example of including a default figure to use with dash-chart-editor

Note that it's necessary to add the source reference to the default figure.
In this example, it's a scatter, so the `xsrc` and `ysrc` are required.

  - `xsrc` – Sets the source reference on dash-chart-editor for x.
  - `ysrc` – Sets the source reference on dash-chart-editor for y.

Be sure to include the correct source reference for the figure type.
E.g., for pie, it’s `labelssrc` and `valuessrc`.  For maps, it’s `locationssrc` and `zsrc`, or `latsrc`, `lonsrc`, etc.
See the Plotly reference docs for more information. https://plotly.github.io/plotly.py-docs/plotly.graph_objects.html
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
    template="plotly_white",
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
