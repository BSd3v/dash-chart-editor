import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import pandas as pd
import plotly.express as px
from inspect import getmembers, isclass, getfullargspec, isfunction
import traceback
import re
import numpy as np

df = px.data.iris()


def rms(values):
    return np.sqrt(sum(values**2)/len(values))

funcReplace = {'avg': 'mean', 'mode': lambda x: x.value_counts().index[0],
               'rms': rms, 'stddev': 'std', 'range': np.ptp}

def camelcaseSnake(name):
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return name

def aggregate(t, df, returnstring, ysrc, xsrc):
    aggs = {}
    aggs_fallback = {}
    if 'aggregations' in t:
        aggs[ysrc] = t['aggregations'][0]['func']
        aggs_fallback[ysrc] = t['aggregations'][0]['func']
        if aggs[ysrc] in funcReplace:
            aggs[ysrc] = funcReplace[aggs[ysrc]]
    else:
        aggs[ysrc] = 'first'

    try:
        returnstring += 'df = df.groupby("' + xsrc + f'").agg({json.dumps(aggs)}).reset_index()'
    except:
        returnstring += 'df = df.groupby("' + json.dumps(xsrc) + f'").agg({json.dumps(aggs_fallback)}).reset_index()'
    try:
        df = df.groupby(xsrc).agg(aggs).reset_index()
    except:
        print(traceback.format_exc())
        pass
    return returnstring + '\n', df

def groupby(t, df, returnstring, ysrc, xsrc):
    ## pass through as this splits into multiple traces
    return returnstring, df

def sort(t, df, returnstring, ysrc, xsrc):
    ## pass through as this groups to apply a sort order
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

typeDataSource = {'pie': {'xsrc': 'labelssrc', 'ysrc': 'valuesrc'},
                    'choropleth': {'xsrc': 'locationssrc', 'ysrc': 'zsrc'},
                    'scattergeo': {'xsrc': 'locationssrc', 'ysrc': 'zsrc'},
                    'scattergeolat': {'xsrc': 'latsrc', 'ysrc': 'zsrc'},
                    'scattermapboxlat': {'xsrc': 'latsrc', 'ysrc': 'zsrc'},
                    'densitymapboxlat': {'xsrc': 'latsrc', 'ysrc': 'zsrc'},
                    'choroplethmapbox': {'xsrc': 'locationssrc', 'ysrc': 'zsrc'}
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
        else:
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

transformsFunctions = {'aggregate': aggregate, 'groupby': groupby, 'filter': filter, 'sort': sort}

figure = {"data": [{"type": "scatter", "mode": "markers", "xsrc": "sepal_length",
                    "transforms": [{"type": "aggregate", "groupssrc": "sepal_length",
                                    "aggregations": [{"func": "first", "target": "x", "enabled": True},
                                                     {"func": "sum", "target": "y", "enabled": True}]}], "ysrc": "sepal_width"}],
          "layout": {"xaxis": {"range": [4.090718396138852, 8.109281603861147], "autorange": True, "type": "linear"},
                     "yaxis": {"range": [0.37124079915878005, 33.22875920084122], "autorange": True, "type": "linear"},
                     "autosize": True, "mapbox": {"style": "open-street-map"},
                     "hovermode": "closest",
                     "annotations": [{"text": "new text", "x": 5.899517356599221, "y": 3.0389957939011567}]},
          "frames": []}


def parseTransforms(transforms, returnstring, ysrc, xsrc, df=pd.DataFrame()):
    sorts = []
    for y in ['filter', 'sort', 'aggregate']:
        for t in transforms:
            if t['type'] == y:
                if 'enabled' in t:
                    if t['enabled']:
                        if t['type'] == 'sort':
                            sorts.append(t)
                        returnstring, df = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
                else:
                    if t['type'] == 'sort':
                        sorts.append(t)
                    returnstring, df = transformsFunctions[t['type']](t, df, returnstring, ysrc, xsrc)
                df.reset_index()
    return returnstring, df, sorts

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
            returnstring, df, groups, sorts = parseTransforms(chart['transforms'], returnstring, chart['ysrc'], chart['xsrc'])
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
                        if camelcaseSnake(path[x]) in newDict:
                            newDict = newDict[camelcaseSnake(path[x])]
                        elif camelcaseSnake(path[x]).replace('_', '') in newDict:
                            newDict = newDict[camelcaseSnake(path[x]).replace('_', '')]
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
                figureArgs[arg] = chart[arg]
        return dropInvalidFigure(realChart, figureArgs, chart['type'].title())

def makeSubplots(layout):
    xcount = 0
    xdomains = []
    ycount = 0
    ydomains = []
    xspecs = []
    yspecs = []
    for l in layout:
        if 'axis' in l:
            if 'xaxis' in l:

                if 'domain' in layout[l]:
                    if layout[l]['domain'] not in xdomains:
                        xdomains.append(layout[l]['domain'])
                        xcount += 1
                else:
                    if xcount < 1:
                        xcount = 1
            elif 'yaxis' in l:
                if 'domain' in layout[l]:
                    if layout[l]['domain'] not in ydomains:
                        ydomains.append(layout[l]['domain'])
                        ycount += 1
                else:
                    if ycount < 1:
                        ycount = 1
    # print(layout)
    # print(ycount, xcount)
    return make_subplots(rows=ycount, cols=xcount)

def chartToPython(figure, df):
    try:
        data = json.loads(figure)['data']
    except:
        data = figure['data']
    fig = makeSubplots(figure['layout'])
    returnstring = ''
    for chart in data:
        dff = df.copy()
        if not 'yaxis' in chart:
            chart['yaxis'] = 'y'
        if not 'xaxis' in chart:
            chart['xaxis'] = 'x'
        if 'ysrc' in chart:
            ysrc = chart['ysrc']
        if 'xsrc' in chart:
            xsrc = chart['xsrc']
        if chart['type'] in typeDataSource:
            if 'latsrc' in chart:
                if typeDataSource[chart['type']+'lat']['xsrc'] in chart:
                    xsrc = chart[typeDataSource[chart['type']+'lat']['xsrc']]
                if typeDataSource[chart['type']+'lat']['ysrc'] in chart:
                    ysrc = chart[typeDataSource[chart['type']+'lat']['ysrc']]
            else:
                if typeDataSource[chart['type']]['xsrc'] in chart:
                    xsrc = chart[typeDataSource[chart['type']]['xsrc']]
                if typeDataSource[chart['type']]['ysrc'] in chart:
                    ysrc = chart[typeDataSource[chart['type']]['ysrc']]

        if 'transforms' in chart:
            groups = []
            for t in chart['transforms']:
                if 'groupssrc' in t:
                    if 'enabled' in t:
                        if t['enabled']:
                            if t['type'] == 'groupby':
                                groups.append(t)
                    else:
                        if t['type'] == 'groupby' and t['groupssrc']:
                            groups.append(t)
            if groups:
                for grp in groups:
                    for x in grp['styles']:
                        dff2 = dff.copy()
                        dff2 = dff2[dff2[grp['groupssrc']] == x['target']]
                        returnstring, dff2, sorts = parseTransforms(chart['transforms'], returnstring, ysrc, xsrc, dff2)

                        dff2.reset_index()
                        if sorts:
                            newSort = []
                            order = []
                            for sort in sorts:
                                if 'targetsrc' in sort:
                                    newSort.append(sort['targetsrc'])
                                else:
                                    newSort.append(xsrc)
                                if 'order' in sort:
                                    if sort['order'] == 'descending':
                                        order.append(False)
                                    else:
                                        order.append(True)
                                else:
                                    order.append(True)
                            if newSort:
                                dff2 = dff2.sort_values(by=newSort, ascending=order)

                        if x['value']:
                            if 'name' not in x['value']:
                                x['value']['name'] = x['target']
                            newchart = parseChartKeys_fig(chart, dff2, x['value'])
                        else:
                            newchart = parseChartKeys_fig(chart, dff2, {'name': x['target']})
                        fig.add_trace(newchart)
            else:
                returnstring, dff, sorts = parseTransforms(chart['transforms'], returnstring, ysrc, xsrc, dff)

                if sorts:
                    newSort = []
                    order = []
                    for sort in sorts:
                        if 'targetsrc' in sort:
                            newSort.append(sort['targetsrc'])
                        else:
                            newSort.append(xsrc)
                        if 'order' in sort:
                            if sort['order'] == 'descending':
                                order.append(False)
                            else:
                                order.append(True)
                        else:
                            order.append(True)
                    if newSort:
                        dff = dff.sort_values(by=newSort, ascending=order)

                newchart = parseChartKeys_fig(chart, dff)
                fig.add_trace(newchart)


        else:
            newchart = parseChartKeys_fig(chart, dff)
            fig.add_trace(newchart)
    fig.update_layout(template='none')
    fig = dropInvalidLayout(figure['layout'], fig)
    return fig

def cleanDataFromFigure(figure):
    cleaning = ['x', 'y', 'z', 'values', 'meta', 'labels', 'locations', 'lat', 'lon', 'open', 'close', 'low', 'high',
                'target']
    for d in figure['data']:
        for k in cleaning:
            if k in d.keys():
                del d[k]
        if 'transforms' in d:
            for t in d['transforms']:
                for k in cleaning:
                    if k in t.keys():
                        del t[k]
    return figure