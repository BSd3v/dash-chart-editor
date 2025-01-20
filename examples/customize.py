"""
Example of ways to customize DashChartEditor
- add a logo with `logoSrc`
- only allow certain figure types with `traceOptions`
- set graph mode bar menu with `config`.  See all the options https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js.

"""


import dash_chart_editor as dce
from dash import Dash, html
import plotly.express as px


app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.35.2.min.js"])

df = px.data.gapminder()

app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo with the Plotly Gapminder dataset"),
        dce.DashChartEditor(
            dataSources=df.to_dict("list"),
            logoSrc="https://busybee.alliancebee.com/static/logo.png",
            config={
                "editable": True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "drawopenpath",
                    "drawclosedpath",
                    "drawcircle",
                    "drawrect",
                    "eraseshape",
                ],
            },
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
