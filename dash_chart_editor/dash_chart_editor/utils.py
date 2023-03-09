import plotly.graph_objs as go
import json
import pandas as pd
import plotly.express as px
from inspect import getmembers, isclass, getfullargspec, isfunction
import traceback
import re

df = px.data.iris()

funcReplace = {'avg': 'mean', 'mode': pd.Series.mode, 'change': 'diff'}

def camelcaseSnake(name):
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return name

def aggregate(t, df, returnstring, ysrc, xsrc):
    print(t)
    aggs = {}
    aggs_fallback = {}
    if t['groupssrc']:
        groupssrc = t['groupssrc']
        if 'aggregations' in t:
            xfunc_orig = t["aggregations"][0]["func"]
            xfunc = xfunc_orig
            if xfunc_orig in funcReplace:
                xfunc = funcReplace[xfunc_orig]
            if groupssrc != xsrc or xfunc_orig != 'first':
                aggs[xsrc] = xfunc
                aggs_fallback[xsrc] = xfunc_orig
            if len(t["aggregations"]) > 1:
                yfunc_orig = t["aggregations"][1]["func"]
                yfunc = yfunc_orig
                if yfunc_orig in funcReplace:
                    yfunc = funcReplace[yfunc]
                if groupssrc != ysrc or yfunc_orig != 'first':
                    aggs[ysrc] = yfunc
                    aggs_fallback[ysrc] = yfunc_orig
            else:
                if groupssrc != ysrc:
                    aggs[ysrc] = 'first'
                    aggs_fallback[ysrc] = 'first'
        else:
            if groupssrc != xsrc:
                aggs[xsrc] = 'first'
            if groupssrc != ysrc:
                aggs[ysrc] = 'first'

    else:
        groupssrc = xsrc
        if 'aggregations' in t:
            yfunc_orig = t["aggregations"][0]["func"]
            yfunc = yfunc_orig
            if yfunc_orig in funcReplace:
                yfunc = funcReplace[yfunc]
            aggs[ysrc] = yfunc
            aggs_fallback[ysrc] = yfunc_orig
        else:
            aggs[ysrc] = 'first'
            aggs_fallback[ysrc] = 'first'
    try:
        returnstring += 'df = df.groupby("' + groupssrc + f'").agg({json.dumps(aggs)}).reset_index()'
    except:
        returnstring += 'df = df.groupby("' + json.dumps(groupssrc) + f'").agg({json.dumps(aggs_fallback)}).reset_index()'
    try:
        df = df.groupby(groupssrc).agg(aggs).reset_index()
    except Exception as e:
        print(str(e))
        if "cannot insert" in str(e) and "already exists" in str(e):
            try:
                df1 = df.groupby(ysrc).agg({xsrc: xfunc}).reset_index()
                df2 = df.groupby(xsrc).agg({ysrc: yfunc}).reset_index()
                df = pd.concat([df1, df2])
            except:
                print(traceback.format_exc())
        else:
            print(traceback.format_exc())
        pass
    return returnstring + '\n', df

def groupby(t, df, returnstring, ysrc, xsrc):
    ## pass through as this splits into multiple traces
    return returnstring, df

operators = {
    '>=': 'ge',
     '<=':'le',
     '<': 'lt',
     '>': 'gt',
     '!=': 'ne',
     '=': 'eq'
    }

inRngOperators = {
    '[]': {'inclusive': 'both'},
    '()': {'inclusive': 'neither'},
    '[)': {'inclusive': 'left'},
    '(]': {'inclusive': 'right'},
}

exRngOperators = {
    '][': {'inclusive': 'neither'},
    ')(': {'inclusive': 'both'},
    '](': {'inclusive': 'right'},
    ')[': {'inclusive': 'left'},
}

otOps = {
    '{}': 'isin'
}

def filter(t, df, returnstring, ysrc, xsrc):
    try:
        v = ''
        op = '='
        if 'value' in t:
            if t['value']:
                v = t['value']
                if 'operation' in t:
                    op = t['operation']
        if t['targetsrc']:
            if isinstance(v, list):
                v = pd.Series(v).astype(df[t['targetsrc']].dtype)
            else:
                if v:
                    v = pd.Series([v]).astype(df[t['targetsrc']].dtype)
                else:
                    v = pd.Series([None]).astype(df[t['targetsrc']].dtype)
            if op in inRngOperators or op in exRngOperators:
                if len(v) > 1:
                    v1 = v.iat[0]
                    v2 = v.iat[1]
                else:
                    v1 = v.iat[0]
                    v2 = v.iat[0]
            elif op in operators:
                v = v.iat[0]
            else:
                v = v.tolist()
            if op in operators:
                df = df.loc[getattr(df[t['targetsrc']], operators[op])(v)]
            elif op in inRngOperators:
                df = df.loc[df[t['targetsrc']].between(v1, v2, **inRngOperators[op])]
            elif op in exRngOperators:
                df = df.loc[~df[t['targetsrc']].between(v1, v2, **exRngOperators[op])]
            else:
                if op == '{}':
                    df = df.loc[df[t['targetsrc']].isin(v)]
                elif op == '}{':
                    df = df.loc[~df[t['targetsrc']].isin(v)]
    except:
        df = pd.DataFrame(columns=df.columns)
        print(traceback.format_exc())
        print(t)
    return returnstring, df

transformsFunctions = {'aggregate': aggregate, 'groupby': groupby, 'filter': filter}

figure = {"data": [{"type": "scatter", "mode": "markers", "meta": {"columnNames": {"x": "sepal_length", "y": "sepal_width"}}, "x": [5.1, 4.9, 4.7, 4.6, 5, 5.4, 4.6, 5, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5, 5, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5, 5.5, 4.9, 4.4, 5.1, 5, 4.5, 4.4, 5, 5.1, 4.8, 5.1, 4.6, 5.3, 5, 7, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5, 5.9, 6, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6, 5.7, 5.5, 5.5, 5.8, 6, 5.4, 6, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1, 5.8, 5, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6, 6.9, 5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7, 6.3, 6.4, 6, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9], "xsrc": "sepal_length", "transforms": [{"type": "aggregate", "groupssrc": "sepal_length", "groups": [5.1, 4.9, 4.7, 4.6, 5, 5.4, 4.6, 5, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5, 5, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5, 5.5, 4.9, 4.4, 5.1, 5, 4.5, 4.4, 5, 5.1, 4.8, 5.1, 4.6, 5.3, 5, 7, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5, 5.9, 6, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6, 5.7, 5.5, 5.5, 5.8, 6, 5.4, 6, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1, 5.8, 5, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6, 6.9, 5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7, 6.3, 6.4, 6, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9], "meta": {"columnNames": {"groups": "sepal_length"}}, "aggregations": [{"func": "first", "target": "x", "enabled": True}, {"func": "sum", "target": "y", "enabled": True}]}], "y": [3.5, 3, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1, 3.7, 3.4, 3, 3, 4, 4.4, 3.9, 3.5, 3.8, 3.8, 3.4, 3.7, 3.6, 3.3, 3.4, 3, 3.4, 3.5, 3.4, 3.2, 3.1, 3.4, 4.1, 4.2, 3.1, 3.2, 3.5, 3.1, 3, 3.4, 3.5, 2.3, 3.2, 3.5, 3.8, 3, 3.8, 3.2, 3.7, 3.3, 3.2, 3.2, 3.1, 2.3, 2.8, 2.8, 3.3, 2.4, 2.9, 2.7, 2, 3, 2.2, 2.9, 2.9, 3.1, 3, 2.7, 2.2, 2.5, 3.2, 2.8, 2.5, 2.8, 2.9, 3, 2.8, 3, 2.9, 2.6, 2.4, 2.4, 2.7, 2.7, 3, 3.4, 3.1, 2.3, 3, 2.5, 2.6, 3, 2.6, 2.3, 2.7, 3, 2.9, 2.9, 2.5, 2.8, 3.3, 2.7, 3, 2.9, 3, 3, 2.5, 2.9, 2.5, 3.6, 3.2, 2.7, 3, 2.5, 2.8, 3.2, 3, 3.8, 2.6, 2.2, 3.2, 2.8, 2.8, 2.7, 3.3, 3.2, 2.8, 3, 2.8, 3, 2.8, 3.8, 2.8, 2.8, 2.6, 3, 3.4, 3.1, 3, 3.1, 3.1, 3.1, 2.7, 3.2, 3.3, 3, 2.5, 3, 3.4, 3], "ysrc": "sepal_width"}], "layout": {"xaxis": {"range": [4.090718396138852, 8.109281603861147], "autorange": True, "type": "linear"}, "yaxis": {"range": [0.37124079915878005, 33.22875920084122], "autorange": True, "type": "linear"}, "autosize": True, "mapbox": {"style": "open-street-map"}, "hovermode": "closest", "annotations": [{"text": "new text", "x": 5.899517356599221, "y": 3.0389957939011567}]}, "frames": []}


def parseTransforms(transforms, returnstring, ysrc, xsrc, df=pd.DataFrame()):
    groups = []
    for t in transforms:
        if 'enabled' in t:
            if t['enabled']:
                if t['type'] == 'groupby':
                    groups.append(t)
                returnstring, df = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
        else:
            if t['type'] == 'groupby' and t['groupssrc']:
                groups.append(t)
            returnstring, df = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
    return returnstring, df, groups

def parseChartKeys_string(chart):
    realChart = None
    for i, y in getmembers(go, isclass):
        if i == chart['type'].title():
            realChart = y
            break
    if realChart:
        returnstring = 'data = go.' + chart['type'].title() + "("
        for arg in getfullargspec(realChart)[0]:
            if arg in chart and arg+'src' not in chart and 'src' not in arg and arg not in ['meta']:
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
            elif arg+'src' not in chart and arg in chart and arg not in ['meta']:
                if chart[arg]:
                    if isinstance(chart[arg], list):
                        returnstring += arg.replace('src', '') + '=df' + json.dumps(chart[arg]) + ', '
                    else:
                        try:
                            returnstring += arg.replace('src', '') + '=df["' + chart[arg] + '"], '
                        except:
                            returnstring += arg.replace('src', '') + '=df[' + json.dumps(chart[arg]) + '], '
        return returnstring[:-2]+')\n'

def chartToPython_string(figure):
    try:
        data = json.loads(figure)['data']
    except:
        data = figure['data']
    returnstring = "fig = go.Figure()\n"
    for chart in data:
        if 'transforms' in chart:
            returnstring, df, groups = parseTransforms(chart['transforms'], returnstring, chart['ysrc'], chart['xsrc'])
        returnstring += parseChartKeys_string(chart)
        returnstring += "fig.add_trace(data)\n"
    returnstring += "fig.update_layout(template='none')\n"
    returnstring += f"fig.update_layout({figure['layout']})\n"
    returnstring += "fig.show()"
    return returnstring

def dropInvalidLayout(layout, fig):
    failed = True
    while failed:
        try:
            fig.update_layout(**layout)
            failed = False
        except Exception as e:
            if 'Invalid property specified for object of type ' in str(e):
                path = str(e).split('plotly.graph_objs.layout.')[1].split(':')[0].split('.')
                key = str(e).split("'")[1]
                newDict = layout
                x = 0
                try:
                    while x < len(path):
                        newDict = newDict[camelcaseSnake(path[x])]
                        x += 1

                    del newDict[key]
                except:
                    print(layout)
                    print(traceback.format_exc())
                    failed = False
            else:
                failed = False
    return fig

def dropInvalidFigure(chart, args, type):
    failed = True
    fig = go.Scatter()
    while failed:
        try:
            fig = chart(**args)
            failed = False
        except Exception as e:
            if 'Invalid property specified for object of type ' in str(e):
                path = str(e).split('plotly.graph_objs.'+type+'.')[1].split(':')[0].split('.')
                key = str(e).split("'")[1]
                newDict = args
                x = 0
                try:

                    while x < len(path):
                        newDict = newDict[camelcaseSnake(path[x])]
                        x += 1

                    del newDict[key]
                except:
                    print(traceback.format_exc())
                    print(path)
                    print(newDict)
                    failed = False
            else:
                failed = False
    return fig

def parseChartKeys_fig(chart, df, figureArgs={}):
    realChart = None
    figureArgs = figureArgs
    for i, y in getmembers(go, isclass):
        if i == chart['type'].title():
            realChart = y
            break
    if realChart:
        chartArgs = getfullargspec(realChart)[0]
        dropping = []
        for arg in figureArgs.keys():
            if arg not in chartArgs:
                dropping.append(arg)
        for i in dropping:
            del figureArgs[i]
        for arg in chartArgs:
            if arg in chart and arg+'src' not in chart and 'src' not in arg and arg not in 'meta':
                figureArgs[arg] = chart[arg]
            elif arg+'src' not in chart and arg in chart and arg not in ['meta']:
                figureArgs[arg.replace('src', '')] = df[chart[arg]]
        return dropInvalidFigure(realChart, figureArgs, chart['type'].title())

def chartToPython(figure, df):
    try:
        data = json.loads(figure)['data']
    except:
        data = figure['data']
    fig = go.Figure()
    returnstring = ''
    for chart in data:
        dff = df.copy()
        if 'transforms' in chart:
            returnstring, dff, groups = parseTransforms(chart['transforms'], returnstring, chart['ysrc'], chart['xsrc'], dff)

            if groups:
                for grp in groups:
                    for x in grp['styles']:
                        dff2 = dff.copy()
                        dff2 = dff2[dff2[grp['groupssrc']] == x['target']]
                        if x['value']:
                            if 'name' not in x['value']:
                                x['value']['name'] = x['target']
                            data = parseChartKeys_fig(chart, dff2, x['value'])
                        else:
                            data = parseChartKeys_fig(chart, dff2, {'name': x['target']})
                        fig.add_trace(data)
            else:
                data = parseChartKeys_fig(chart, dff)
                fig.add_trace(data)
        else:
            data = parseChartKeys_fig(chart, dff)
            fig.add_trace(data)
    fig.update_layout(template='none')
    fig = dropInvalidLayout(figure['layout'], fig)
    return fig