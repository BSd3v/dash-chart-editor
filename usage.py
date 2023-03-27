import traceback

import dash_chart_editor as dce
from dash import Dash, callback, html, Input, Output, dcc
import plotly.express as px
import plotly.graph_objs as go
import json
import traceback
from pprint import pprint
import yfinance as yf

app = Dash(__name__,
           external_scripts=['https://cdn.plot.ly/plotly-2.18.2.min.js'])

df = yf.download('AAPL', period="30d", interval="30m", prepost=False)

df.reset_index(inplace=True)

app.layout = html.Div([
    dce.DashChartEditor(
        id='test',
        dataSources=df.to_dict('list'),
        style={'width': '100vw', 'height': '50vh'},
        #loadFigure=figure,
        traceOptions=['scatter', 'scattergeo', 'candlestick', 'bar'],
        logoSrc="https://busybee.alliancebee.com/static/logo.png",
        config={'editable': True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "drawopenpath",
                    "drawclosedpath",
                    "drawcircle",
                    "drawrect",
                    "eraseshape",
                ]
                }
    ),
    html.Div(id='output')
])

@app.callback(
    Output('output','children'),
    Input('test', 'figure'),
)
def outputData(figure):
    if figure:
        # cleaning data output for unnecessary columns
        figure = dce.cleanDataFromFigure(figure)
        print(figure)
        dff = df.copy()
        try:
            #pprint(dce.chartToPython_string({'data': data, 'layout': layout, 'frames': frames}))
            fig = dcc.Graph(figure=dce.chartToPython(figure, dff))
            return fig
        except:
            print(traceback.format_exc())
            pass
        return json.dumps(figure)\
            .replace('true','True')\
            .replace('false', 'False')\
            .replace('null', 'None')


if __name__ == '__main__':
    app.run_server(debug=True)
