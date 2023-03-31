"""
This demos saving the figure edited in dash-chart-editor and displaying the figure code
"""


import dash_chart_editor as dce
from dash import Dash, html, dcc, Input, Output, no_update
import pandas as pd
import dash_bootstrap_components as dbc

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app = Dash(__name__,
           external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"],
           external_stylesheets=[dbc.themes.BOOTSTRAP]
           )

chart_editor =  dbc.Card(
        dce.DashChartEditor(
        id="chart-editor",
        dataSources=df.to_dict("list"),
        )
)

code = dbc.Card(
    [
        dbc.CardHeader(dbc.Button("Update Code", id="save")),
        dbc.CardBody( html.Pre(id="output"), style={"minHeight": 200})
    ],
    className="my-4"
)

app.layout = dbc.Container(
    [
        html.H4("Dash Chart Editor Demo with the Plotly Solar dataset", className="text-center p-2"),
        chart_editor,
        code
    ],
)

@app.callback(
    Output("chart-editor", "saveState"),
    Input("save", "n_clicks")
)
def save_figure(n):
    return True


@app.callback(
    Output('output','children'),
    Input('chart-editor', 'figure'),
)
def send_fig_to_dcc(figure):
    if figure:
        # cleaning data output for unnecessary columns
        figure = dce.cleanDataFromFigure(figure)

        # create Figure object from dash-chart-editor figure
        figure = dce.chartToPython(figure, df)
        return str(figure)
    return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
