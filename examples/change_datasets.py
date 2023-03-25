import dash_chart_editor as dce
from dash import Dash, html, Output, Input, dcc, no_update
import plotly.express as px


app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])


datasets = {
    "tips": px.data.tips().to_dict("list"),
    "gapminder": px.data.gapminder().to_dict("list"),
    "iris": px.data.iris().to_dict("list"),
    "stocks": px.data.stocks().to_dict("list"),
}

dropdown = dcc.Dropdown(
    id="dataset",
    options=list(datasets.keys()),
    value="tips",
    clearable=False,
    style={"marginBottom": 20, "maxWidth": 430},
)

app.layout = html.Div(
    [
        html.H4("Dash Chart Editor Demo with selected dataset"),
        dropdown,
        dce.DashChartEditor(
            dataSources=px.data.tips().to_dict("list"), id="chartEditor"
        ),
    ]
)


@app.callback(
    Output("chartEditor", "dataSources"),
    Input("dataset", "value"),
)
def set_dataset(v):
    return datasets[v]


if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
