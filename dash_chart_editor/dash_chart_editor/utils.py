import plotly.graph_objs as go
import json
import pandas as pd
import plotly.express as px
from inspect import getmembers, isclass, getfullargspec

df = px.data.iris()

def aggregate(t, df, returnstring, ysrc, xsrc):
    xfunc = t["aggregations"][0]["func"]
    yfunc = t["aggregations"][1]["func"]
    if xfunc == 'first':
        returnstring += 'df = df.groupby("' + xsrc + f'").{yfunc}().reset_index()'
    else:
        returnstring += 'df = df.agg({"' + xsrc + '": "' + xfunc + '", "'\
            + ysrc + '": "' + yfunc + '"}).groupby("' + xsrc + '").reset_index()'
    return returnstring + '\n'

transformsFunctions = {'aggregate': aggregate}

figure = {"data": [{"type": "scatter", "mode": "markers", "meta": {"columnNames": {"x": "sepal_length", "y": "sepal_width"}}, "x": [5.1, 4.9, 4.7, 4.6, 5, 5.4, 4.6, 5, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5, 5, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5, 5.5, 4.9, 4.4, 5.1, 5, 4.5, 4.4, 5, 5.1, 4.8, 5.1, 4.6, 5.3, 5, 7, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5, 5.9, 6, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6, 5.7, 5.5, 5.5, 5.8, 6, 5.4, 6, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1, 5.8, 5, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6, 6.9, 5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7, 6.3, 6.4, 6, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9], "xsrc": "sepal_length", "transforms": [{"type": "aggregate", "groupssrc": "sepal_length", "groups": [5.1, 4.9, 4.7, 4.6, 5, 5.4, 4.6, 5, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5, 5, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5, 5.5, 4.9, 4.4, 5.1, 5, 4.5, 4.4, 5, 5.1, 4.8, 5.1, 4.6, 5.3, 5, 7, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5, 5.9, 6, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6, 5.7, 5.5, 5.5, 5.8, 6, 5.4, 6, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1, 5.8, 5, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6, 6.9, 5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7, 6.3, 6.4, 6, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9], "meta": {"columnNames": {"groups": "sepal_length"}}, "aggregations": [{"func": "first", "target": "x", "enabled": True}, {"func": "sum", "target": "y", "enabled": True}]}], "y": [3.5, 3, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1, 3.7, 3.4, 3, 3, 4, 4.4, 3.9, 3.5, 3.8, 3.8, 3.4, 3.7, 3.6, 3.3, 3.4, 3, 3.4, 3.5, 3.4, 3.2, 3.1, 3.4, 4.1, 4.2, 3.1, 3.2, 3.5, 3.1, 3, 3.4, 3.5, 2.3, 3.2, 3.5, 3.8, 3, 3.8, 3.2, 3.7, 3.3, 3.2, 3.2, 3.1, 2.3, 2.8, 2.8, 3.3, 2.4, 2.9, 2.7, 2, 3, 2.2, 2.9, 2.9, 3.1, 3, 2.7, 2.2, 2.5, 3.2, 2.8, 2.5, 2.8, 2.9, 3, 2.8, 3, 2.9, 2.6, 2.4, 2.4, 2.7, 2.7, 3, 3.4, 3.1, 2.3, 3, 2.5, 2.6, 3, 2.6, 2.3, 2.7, 3, 2.9, 2.9, 2.5, 2.8, 3.3, 2.7, 3, 2.9, 3, 3, 2.5, 2.9, 2.5, 3.6, 3.2, 2.7, 3, 2.5, 2.8, 3.2, 3, 3.8, 2.6, 2.2, 3.2, 2.8, 2.8, 2.7, 3.3, 3.2, 2.8, 3, 2.8, 3, 2.8, 3.8, 2.8, 2.8, 2.6, 3, 3.4, 3.1, 3, 3.1, 3.1, 3.1, 2.7, 3.2, 3.3, 3, 2.5, 3, 3.4, 3], "ysrc": "sepal_width"}], "layout": {"xaxis": {"range": [4.090718396138852, 8.109281603861147], "autorange": True, "type": "linear"}, "yaxis": {"range": [0.37124079915878005, 33.22875920084122], "autorange": True, "type": "linear"}, "autosize": True, "mapbox": {"style": "open-street-map"}, "hovermode": "closest", "annotations": [{"text": "new text", "x": 5.899517356599221, "y": 3.0389957939011567}]}, "frames": []}


def parseTransforms(transforms, returnstring, ysrc, xsrc, df=pd.DataFrame()):
    for t in transforms:
        if 'enabled' in t:
            if t['enabled']:
                returnstring = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
        else:
            returnstring = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
    return returnstring

def parseChartKeys(chart):
    realChart = None
    for i, y in getmembers(go, isclass):
        if i == chart['type'].title():
            realChart = y
            break
    if realChart:
        returnstring = 'data = go.' + chart['type'].title() + "("
        for arg in getfullargspec(realChart)[0]:
            if arg in chart and arg not in ['x', 'y', 'values', 'labels', 'meta'] and 'src' not in arg:
                if isinstance(chart[arg], bool):
                    if chart[arg]:
                        returnstring += arg + '=True, '
                    else:
                        returnstring += arg + '=False, '
                elif chart[arg]:
                    if isinstance(chart[arg], list):
                        returnstring += arg + '=' + json.dumps(chart[arg]) + ', '
                    else:
                        try:
                            returnstring += arg + '="' + chart[arg] + '", '
                        except:
                            returnstring += arg + '=' + json.dumps(chart[arg]) + ', '
                else:
                    returnstring += arg + '=None, '
            elif arg+'src' in chart:
                returnstring += arg+'=df["' + chart[arg+'src'] + '"], '
        return returnstring[:-2]+')\n'

def chartToPython(figure):
    try:
        data = json.loads(figure)['data']
    except:
        data = figure['data']
    returnstring = "fig = go.Figure()\n"
    for chart in data:
        if 'transforms' in chart:
            returnstring = parseTransforms(chart['transforms'], returnstring, chart['ysrc'], chart['xsrc'])
        returnstring += parseChartKeys(chart)
        returnstring += "fig.add_trace(data)\n"
    returnstring += "fig.update_layout(template='none')\n"
    returnstring += f"fig.update_layout({figure['layout']})\n"
    returnstring += "fig.show()"
    return returnstring