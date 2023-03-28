import dash_chart_editor as dce
from dash import Dash, html
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])


app.layout = html.Div([
    html.H4("Dash Chart Editor Demo with the Plotly Solar dataset"),
    dce.DashChartEditor(dataSources=df.to_dict("list")),
])


if __name__ == "__main__":
    app.run_server(debug=True)
