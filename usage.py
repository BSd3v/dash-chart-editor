from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, ctx, no_update, Patch
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_chart_editor as dce

df = px.data.gapminder()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dcc.Store(id='oldSum', data=0, storage_type='memory'),
        dbc.Modal([
            dbc.ModalTitle('Customizing Charts'),
            dbc.ModalBody([dcc.Input(id="chartId"),dce.DashChartEditor(dataSources=df.to_dict('list'), id='editor',
                                                                       style={'height': '60vh'})]),
            dbc.ModalFooter([dbc.Button('Save Chart', id='saveEditor'),
                            dbc.Button('Save & Close', id='saveCloseEditor', color='secondary')])
        ], id='editorMenu', size='xl'),
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Pattern Matching Callbacks Demo"),
                    dbc.Button(
                        "Add Chart", id="pattern-match-add-chart", n_clicks=0
                    ),
                    html.Div(id="pattern-match-container", children=[], className="mt-4"),
                ]
            )
        ),
     ],
    fluid=True,
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
                figure=go.Figure()
            ),
        ],
        style={
            "width": 400,
            "display": "inline-block",
        },
        className="m-1",
        id={"type": "dynamic-card", "index": n_clicks},
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
    Output("editorMenu", "is_open"), Output("editor", "loadFigure"), Output('chartId', 'value'),
    Output('oldSum', 'data'),
    Input({"type": "dynamic-edit", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-output", "index": ALL}, "figure"),
    State('oldSum', 'data'),
    prevent_initial_call=True,
)
def remove_card(edit, figs, oldSum):
    if sum(edit) > 0 and sum(edit) != oldSum:
        oldSum = sum(edit)
        x = ctx.triggered_id['index']
        if edit[x] > 0:
            if figs[x]['data']:
                return True, figs[x], x, oldSum
            return True, {'data': [], 'layout': {}}, x, oldSum
    return no_update, no_update, no_update, oldSum

@app.callback(
    Output('editor', 'saveState'),
    Input('saveEditor', 'n_clicks'),
    Input('saveCloseEditor', 'n_clicks'),
)
def saveChart(n, n1):
    if n or n1:
        return True

@app.callback(
    Output("editorMenu", "is_open", allow_duplicate=True),
    Input('saveCloseEditor', 'n_clicks'),
    prevent_initial_call=True
)
def saveChart(n):
    if n:
        return False
    return no_update

@app.callback(
    Output("pattern-match-container", "children", allow_duplicate=True),
    Input('editor', 'figure'), State('chartId', 'value'),
    prevent_initial_call=True
)
def saveToFig(f, v):
    if f:
        print(v)
        figs = Patch()
        figs[v]['figure'] = f
        return figs
    return no_update

if __name__ == "__main__":
    app.run_server(debug=True)