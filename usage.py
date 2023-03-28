import dash_chart_editor as dce
from dash import Dash, callback, html, Input, Output, dcc, no_update
import traceback
import yfinance as yf
import plotly.express as px

app = Dash(__name__,
           external_scripts=['https://cdn.plot.ly/plotly-2.18.2.min.js'])

df = px.data.iris()

# df = yf.download('AAPL', period="5d", interval="5m", prepost=True)

# df.reset_index(inplace=True)
#
# figure = {'data': [{'type': 'candlestick', 'mode': 'markers', 'xsrc': 'Datetime', 'opensrc': 'Open', 'highsrc': 'High', 'lowsrc': 'Low', 'closesrc': 'Adj Close', 'name': 'AAPL'}, {'type': 'bar', 'orientation': 'v', 'xsrc': 'Datetime', 'ysrc': 'Volume', 'yaxis': 'y2', 'texttemplate': '', 'hovertemplate': '', 'name': 'Volume'}], 'layout': {'xaxis': {'range': ['2023-03-23 03:26:16.2544', '2023-03-23 22:20:55.0705'], 'autorange': False, 'title': {'text': 'Datetime'}, 'rangeslider': {'yaxis': {'_template': None, 'rangemode': 'match'}, 'autorange': True, 'range': ['2023-03-21 03:57:30', '2023-03-27 13:27:30'], 'yaxis2': {'_template': None, 'rangemode': 'match'}}, 'showspikes': True, 'type': 'date'}, 'yaxis': {'range': [148.26346833333335, 170.69490166666665], 'autorange': True}, 'autosize': True, 'mapbox': {'style': 'open-street-map'}, 'yaxis2': {'side': 'right', 'overlaying': 'y', 'type': 'linear', 'range': [0, 10000000], 'autorange': False, 'showgrid': False, 'zeroline': False, 'showticklabels': False}, 'dragmode': 'pan', 'hovermode': 'x', 'showlegend': False}, 'frames': []}
#
# fig = dce.chartToPython(figure, df)

app.layout = html.Div([
    dce.DashChartEditor(
        id='test',
        dataSources=df.to_dict('list'),
        style={'width': '100vw', 'height': '50vh'},
        #loadFigure=fig,
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
    # html.Button(id='reset', children='resetting'),
    dcc.Graph(id='output')
])

@app.callback(
    Output('output','figure'),
    Input('test', 'figure'),
)
def outputData(figure):
    if figure:
        # cleaning data output for unnecessary columns
        figure = dce.cleanDataFromFigure(figure)
        try:
            #pprint(dce.chartToPython_string({'data': data, 'layout': layout, 'frames': frames}))
            fig = dce.chartToPython(figure, df)
            return fig
        except:
            print(traceback.format_exc())
            pass
    return no_update

# @app.callback(Output('test', 'loadFigure'),
#               Input('reset', 'n_clicks'))
# def reset(n):
#     if n:
#         return fig


if __name__ == '__main__':
    app.run_server(debug=True)
