import dash_chart_editor as dce
from dash import Dash, html
import plotly.express as px


app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

df = px.data.gapminder()

app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo with the Plotly Gapminder dataset"),
        dce.DashChartEditor(
            dataSources=df.to_dict("list"),
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
