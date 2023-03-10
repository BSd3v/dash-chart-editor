import traceback

import dash_chart_editor as dce
from dash import Dash, callback, html, Input, Output, dcc
import plotly.express as px
import plotly.graph_objs as go
import json
import traceback
from pprint import pprint

app = Dash(__name__,
           external_scripts=['https://cdn.plot.ly/plotly-2.18.2.min.js'])

df = px.data.iris()

figure = {"data": [{"type": "bar", "mode": "markers", "autocolorscale": True,
                    "x": [5.1, 4.9, 4.7, 4.6, 5, 5.4, 4.6, 5, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5, 5, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5, 5.5, 4.9, 4.4, 5.1, 5, 4.5, 4.4, 5, 5.1, 4.8, 5.1, 4.6, 5.3, 5, 7, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5, 5.9, 6, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6, 5.7, 5.5, 5.5, 5.8, 6, 5.4, 6, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1, 5.8, 5, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6, 6.9, 5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7, 6.3, 6.4, 6, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9], "xsrc": "sepal_length", "meta": {"columnNames": {"x": "sepal_length", "y": "species", "z": "petal_length"}}, "y": ["setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "setosa", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "versicolor", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica", "virginica"], "ysrc": "species", "z": [[1.4], [1.4], [1.3], [1.5], [1.4], [1.7], [1.4], [1.5], [1.4], [1.5], [1.5], [1.6], [1.4], [1.1], [1.2], [1.5], [1.3], [1.4], [1.7], [1.5], [1.7], [1.5], [1], [1.7], [1.9], [1.6], [1.6], [1.5], [1.4], [1.6], [1.6], [1.5], [1.5], [1.4], [1.5], [1.2], [1.3], [1.5], [1.3], [1.5], [1.3], [1.3], [1.3], [1.6], [1.9], [1.4], [1.6], [1.4], [1.5], [1.4], [4.7], [4.5], [4.9], [4], [4.6], [4.5], [4.7], [3.3], [4.6], [3.9], [3.5], [4.2], [4], [4.7], [3.6], [4.4], [4.5], [4.1], [4.5], [3.9], [4.8], [4], [4.9], [4.7], [4.3], [4.4], [4.8], [5], [4.5], [3.5], [3.8], [3.7], [3.9], [5.1], [4.5], [4.5], [4.7], [4.4], [4.1], [4], [4.4], [4.6], [4], [3.3], [4.2], [4.2], [4.2], [4.3], [3], [4.1], [6], [5.1], [5.9], [5.6], [5.8], [6.6], [4.5], [6.3], [5.8], [6.1], [5.1], [5.3], [5.5], [5], [5.1], [5.3], [5.5], [6.7], [6.9], [5], [5.7], [4.9], [6.7], [4.9], [5.7], [6], [4.8], [4.9], [5.6], [5.8], [6.1], [6.4], [5.6], [5.1], [5.6], [6.1], [5.6], [5.5], [4.8], [5.4], [5.6], [5.1], [5.1], [5.9], [5.7], [5.2], [5], [5.2], [5.4], [5.1]], "zsrc": ["petal_length"]}], "layout": {"autosize": True, "mapbox": {"style": "open-street-map"}, "hovermode": "closest", "annotations": [{"text": "new text", "x": 5.020148050879128, "y": 2.361027251008215}], "xaxis": {"range": [4.9, 5.1], "autorange": True, "type": "linear"}, "yaxis": {"range": [-0.5, 2.649687727163578], "autorange": True, "type": "category"}}, "frames": []}

app.layout = html.Div([
    dce.DashChartEditor(
        id='test',
        dataSources=df.to_dict('list'),
        style={'width': '100vw', 'height': '50vh'},
        loadFigure=figure
    ),
    dcc.RangeSlider(id='filter', min=df['sepal_length'].min(), max=df['sepal_length'].max(), step=0.1),
    html.Div(id='output')
])

@app.callback(
    Output('output','children'),
    Input('test', 'data'),
    Input('test', 'layout'),
    Input('test', 'frames'),
    Input('filter', 'value')
)
def outputData(data, layout, frames, filter):
    if data or layout or frames or filter:
        # cleaning data output for unnecessary columns
        for d in data:
            for k in ['x', 'y', 'z', 'values', 'meta']:
                if k in d.keys():
                    del d[k]
            if 'transforms' in d:
                for t in d['transforms']:
                    for k in ['x', 'y', 'z', 'values', 'meta', 'groups', 'target']:
                        if k in t.keys():
                            del t[k]
        print(data)
        dff = df.copy()
        # if filter:
        #     dff = dff[dff['sepal_length'].between(filter[0], filter[1])]
        try:
            #pprint(dce.chartToPython_string({'data': data, 'layout': layout, 'frames': frames}))
            figure = dcc.Graph(figure=dce.chartToPython({'data': data, 'layout': layout, 'frames': frames}, dff))
            return figure
        except Exception as e:
            print(traceback.format_exc())
            pass
        return json.dumps({'data': data, 'layout': layout, 'frames': frames})\
            .replace('true','True')\
            .replace('false', 'False')\
            .replace('null', 'None')


if __name__ == '__main__':
    app.run_server(debug=True)
