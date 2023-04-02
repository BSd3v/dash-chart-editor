"""
requires dash>=2.9.2

This demo shows how to use the Dash Chart Editor to edit figures that are dynamically added to the layout.

Note that the dynamically generated Edit button triggers a callback whenever a new figure card
is added to the layout.  As a workaround we use the dcc.Store to track n_clicks to see if the
button was clicked.
"""


from dash import Dash,dcc,html,Input,Output,State,MATCH,ALL, ctx, no_update, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_chart_editor as dce
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

chart_editor_modal = dbc.Modal(
    [
        dbc.ModalTitle(["Editing Figure #", html.Span(id="chart-id")]),
        dbc.ModalBody(
            [
                dce.DashChartEditor(
                    dataSources=df.to_dict("list"),
                    id="editor",
                    style={"maxHeight": "50vh"},
                ),
            ]
        ),
        dbc.ModalFooter(
            dbc.Button( "Save & Close", id="save-close", color="secondary"),
        ),
    ],
    id="editor-modal",
    size="xl",
)


def make_card(n_clicks):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    f"Figure {n_clicks + 1} ",
                    dbc.Button(
                        "Edit",
                        id={"type": "dynamic-edit", "index": n_clicks},
                        n_clicks=0,
                        color="info",
                    ),
                    dbc.Button(
                        "X",
                        id={"type": "dynamic-delete", "index": n_clicks},
                        n_clicks=0,
                        color="secondary",
                    ),
                ],
                className="text-end",
            ),
            dcc.Graph(
                id={"type": "dynamic-output", "index": n_clicks},
                style={"height": 400},
                figure=px.bar(df, x="State", y="Number of Solar Plants")
            ),
        ],
        style={
            "width": 400,
            "display": "inline-block",
        },
        className="m-1",
        id={"type": "dynamic-card", "index": n_clicks},
    )


app.layout = dbc.Container(
    [
        html.H3("Dash Chart Editor Demo"),
        dbc.Button("Add Chart", id="pattern-match-add-chart", n_clicks=0),
        html.Div(id="pattern-match-container", children=[], className="mt-4" ),
        dcc.Store(id="oldSum", data=0, storage_type="memory"),
        chart_editor_modal,
    ],
    fluid=True,
)


@app.callback(
    Output("pattern-match-container", "children"),
    Input("pattern-match-add-chart", "n_clicks"),
)
def add_card(n_clicks):
    patched_children = Patch()
    new_card = make_card(n_clicks)
    patched_children.append(new_card)
    return patched_children


@app.callback(
    Output({"type": "dynamic-card", "index": MATCH}, "style"),
    Input({"type": "dynamic-delete", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def remove_card(_):
    return {"display": "none"}


@app.callback(
    Output("editor-modal", "is_open"),
    Output("editor", "loadFigure"),
    Output("chart-id", "children"),
    Output("oldSum", "data"),
    Input({"type": "dynamic-edit", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-output", "index": ALL}, "figure"),
    State("oldSum", "data"),
    prevent_initial_call=True
)
def edit_figure(edit, figs, oldSum):
    if sum(edit) > 0 and sum(edit) != oldSum:
        oldSum = sum(edit)
        x = ctx.triggered_id["index"]
        fig_number = x + 1
        if edit[x] > 0:
            if figs[x]["data"]:
                return True, figs[x], fig_number, oldSum
            return True, {"data": [], "layout": {}}, fig_number, oldSum
    return no_update, no_update, no_update, oldSum


@app.callback(
    Output("editor", "saveState"),
    Output("editor-modal", "is_open", allow_duplicate=True),
    Input("save-close", "n_clicks"),
    prevent_initial_call=True
)
def save_dce_figure(n):
    if n:
        return True, False


@app.callback(
    Output({"type": "dynamic-output", "index": ALL}, "figure"),
    Input("editor", "figure"),
    State("chart-id", "children"),
    State({"type": "dynamic-output", "index": ALL}, "figure"),
)
def save_dcc_graph(f, v, figs):
    if f:
        figs[v-1] = f
    return figs


if __name__ == "__main__":
    app.run_server(debug=True)
