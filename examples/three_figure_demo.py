from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_chart_editor as dce
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True)

chart_editor_modal = dbc.Modal(
    [
        dbc.ModalTitle(["Editing Figure #", html.Span(id="chart-id")]),
        dbc.ModalBody(
            dce.DashChartEditor(
                dataSources=df.to_dict("list"),
                id="chart-editor",
            ),
        ),
        dbc.ModalFooter(dbc.Button("Save & Close", id="save", color="secondary")),
    ],
    id="editor-modal",
    size="xl",
)


def make_card(card_number):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    f"Figure {card_number} ",
                    dbc.Button(
                        "Edit",
                        id=f"edit-{card_number}",
                        color="info",
                    ),
                ],
                className="text-end",
            ),
            dcc.Graph(
                id=f"fig-{card_number}",
                figure=px.bar(df, x="State", y="Number of Solar Plants"),
            ),
        ],
        className="m-1",
    )


app.layout = dbc.Container(
    [
        html.H3("Dash Chart Editor Demo"),
        dbc.Row([dbc.Col(make_card(i)) for i in [1, 2, 3]]),
        chart_editor_modal,
    ],
    fluid=True,
)


@app.callback(
    Output("editor-modal", "is_open"),
    Output("chart-editor", "loadFigure"),
    Output("chart-id", "children"),
    Input("edit-1", "n_clicks"),
    Input("edit-2", "n_clicks"),
    Input("edit-3", "n_clicks"),
    Input("save", "n_clicks"),
    State("fig-1", "figure"),
    State("fig-2", "figure"),
    State("fig-3", "figure"),
)
def edit_fig(edit1, edit2, edit3, save, fig1, fig2, fig3):
    triggered = ctx.triggered_id
    chart_id = triggered[-1]
    if triggered == "save":
        return False, no_update, no_update
    if triggered == "edit-1":
        return True, fig1, chart_id
    if triggered == "edit-2":
        return True, fig2, chart_id
    if triggered == "edit-3":
        return True, fig3, chart_id


@app.callback(
    Output("chart-editor", "saveState"),
    Input("save", "n_clicks"),
)
def update_chart_editor_fig(n):
    return True


@app.callback(
    Output("fig-1", "figure"),
    Output("fig-2", "figure"),
    Output("fig-3", "figure"),
    Input("chart-editor", "figure"),
    State("chart-id", "children"),
)
def save_to_fig(dce_fig, fig_number):
    if fig_number == "1":
        return dce_fig, no_update, no_update
    if fig_number == "2":
        return no_update, dce_fig, no_update
    if fig_number == "3":
        return no_update, no_update, dce_fig


if __name__ == "__main__":
    app.run_server(debug=True)
