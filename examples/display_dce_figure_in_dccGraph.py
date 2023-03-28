"""
This demos saving the figure edited in dash-chart-editor
and displaying it in a dcc.Graph()
"""


import dash_chart_editor as dce
from dash import Dash, html, dcc, Input, Output, no_update
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])


app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo with the Plotly Solar dataset"),
        html.Button("Save Figure", id="save"),
        dce.DashChartEditor(
            id="chart-editor",
            dataSources=df.to_dict("list"),
        ),
        dcc.Graph(id="graph")
    ]
)

@app.callback(
    Output("chart-editor", "saveState"),
    Input("save", "n_clicks")
)
def save_figure(n):
    if n:
        return True


@app.callback(
    Output('graph','figure'),
    Input('chart-editor', 'figure'),
)
def send_fig_to_dcc(figure):
    if figure:
        # cleaning data output for unnecessary columns
        figure = dce.cleanDataFromFigure(figure)

        # create Figure object from dash-chart-editor figure
        figure = dce.chartToPython(figure, df)
        return figure

    return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
