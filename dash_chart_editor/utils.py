import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import pandas as pd
import plotly.express as px
from inspect import getmembers, isclass, getfullargspec, isfunction
import traceback
import re
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

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


def get_offset_date(offset_str):
    """
    Calculate the date offset by a given number of days, months, or years.

    Parameters:
    offset_str (str): A string in the format 'offsetDay(n)', 'offsetMonth(n)', or 'offsetYear(n)' where n is an integer.

    Returns:
    datetime.date: The calculated date.
    """
    day_match = re.match(r'offsetDay\((\-?\d+)\)', offset_str)
    month_match = re.match(r'offsetMonth\((\-?\d+)\)', offset_str)
    year_match = re.match(r'offsetYear\((\-?\d+)\)', offset_str)

    if day_match:
        days_offset = int(day_match.group(1))
        return (datetime.datetime.now() + datetime.timedelta(days=days_offset)).date()
    elif month_match:
        months_offset = int(month_match.group(1))
        return (datetime.datetime.now() + relativedelta(months=months_offset)).date()
    elif year_match:
        years_offset = int(year_match.group(1))
        return (datetime.datetime.now() + relativedelta(years=years_offset)).date()
    else:
        raise ValueError(f"Invalid offset format: {offset_str}")

# Define common date swaps for logistics needs, including rolling periods, cast as dates
date_swaps = {
    'today': datetime.datetime.now().date(),
    'yesterday': (datetime.datetime.now() - datetime.timedelta(days=1)).date(),
    'tomorrow': (datetime.datetime.now() + datetime.timedelta(days=1)).date(),
    'start_of_week': (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).date(),
    'end_of_week': (datetime.datetime.now() + datetime.timedelta(days=(6 - datetime.datetime.now().weekday()))).date(),
    'start_of_month': datetime.datetime.now().replace(day=1).date(),
    'end_of_month': ((datetime.datetime.now().replace(day=1) + relativedelta(months=1)) - datetime.timedelta(days=1)).date(),
    'start_of_year': datetime.datetime.now().replace(month=1, day=1).date(),
    'end_of_year': datetime.datetime.now().replace(month=12, day=31).date(),
    'start_of_last_month': (datetime.datetime.now().replace(day=1) - relativedelta(months=1)).date(),
    'end_of_last_month': (datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)).date(),
    'start_of_next_month': (datetime.datetime.now().replace(day=1) + relativedelta(months=1)).date(),
    'end_of_next_month': ((datetime.datetime.now().replace(day=1) + relativedelta(months=2)) - datetime.timedelta(days=1)).date(),
    'start_of_last_quarter': (datetime.datetime.now() - relativedelta(months=(datetime.datetime.now().month - 1) % 3)).replace(day=1).date(),
    'end_of_last_quarter': ((datetime.datetime.now().replace(day=1) - relativedelta(months=(datetime.datetime.now().month - 1) % 3)) + relativedelta(months=3) - datetime.timedelta(days=1)).date(),
    'start_of_next_quarter': (datetime.datetime.now() + relativedelta(months=(3 - (datetime.datetime.now().month - 1) % 3))).replace(day=1).date(),
    'end_of_next_quarter': ((datetime.datetime.now().replace(day=1) + relativedelta(months=(3 - (datetime.datetime.now().month - 1) % 3)) + relativedelta(months=3)) - datetime.timedelta(days=1)).date(),
}


def convert_to_date(series):
    """
    Convert a Pandas Series to date type, handling errors gracefully.

    Parameters:
    series (pd.Series): The Pandas Series to convert.

    Returns:
    pd.Series: A Series with date-only values.
    """
    try:
        return pd.to_datetime(series, errors='coerce').dt.date
    except Exception as e:
        print(f"Error converting series to date: {e}")
        return series

def process_columns(df, v1, v2, date_swaps, targetsrc):
    v1_series = None
    v2_series = None
    v1_date = False
    # Check if v1 is in date_swaps before converting it to a Series
    if v1 in date_swaps:
        v1_date = True
        v1 = date_swaps[v1]
        # If using date_swap, need to switch to date for the filters
        df[targetsrc] = convert_to_date(df[targetsrc])
    elif 'offset' in v1:
        v1_date = True
        v1 = get_offset_date(v1)
        df[targetsrc] = convert_to_date(df[targetsrc])
    elif v1 in df.columns:
        v1_series = df[v1]
        if v2 in date_swaps:
            v1_series = convert_to_date(v1_series)

    # Check if v2 is in date_swaps before converting it to a Series
    if v2 in date_swaps:
        v2 = date_swaps[v2]
        # If using date_swap, need to switch to date for the filters
        df[targetsrc] = convert_to_date(df[targetsrc])
    elif 'offset' in v2:
        v2 = get_offset_date(v2)
        df[targetsrc] = convert_to_date(df[targetsrc])
    elif v2 in df.columns:
        v2_series = df[v2]
        if v1_date:
            v2_series = convert_to_date(v2_series)

    return df, v1_series if v1_series is not None else v1, v2_series if v2_series is not None else v2

def filter(t, df, returnstring, ysrc, xsrc):
    df = df.fillna('')
    try:
        if t['enabled']:
            v = t.get('value', '')
            op = t.get('operation', '=')
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
                    df, v1, v2 = process_columns(df, v1, v2, date_swaps, t['targetsrc'])
                elif op in operators:
                    v = v.iat[0]
                else:
                    v = v.tolist()
                if v is None:
                    v = ''
                if op in operators:
                    if v in df.columns:
                        v = df[v]
                    elif 'offset' in v:
                        v = get_offset_date(v)
                        ## if using offsetDay, need to switch to date for the filters
                        df[t['targetsrc']] = convert_to_date(df[t['targetsrc']])
                    elif v in date_swaps:
                        v = date_swaps[v]
                        ## if using date_swap, need to switch to date for the filters
                        df[t['targetsrc']] = convert_to_date(df[t['targetsrc']])
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

transformsFunctions = {'aggregate': aggregate, 'groupby': groupby, 'filter': filter, 'filter_python': filter, 'sort': sort}

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
    # only do filters, everything else is handled by the transforms
    for y in ['filter', 'filter_python']:
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
            fig['layout'] = layout
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
    newDict = args
    newDict['arg'] = {}
    while failed:
        try:
            fig = chart(**newDict)
            failed = False
        except Exception as e:
            print('failed')
            print(str(e))
            if 'Invalid property specified for object of type ' in str(e):
                path = str(e).split('plotly.graph_objs.'+type+'.')[1].split(':')[0].split('.')
                key = str(e).split("'")[1]
                x = 0
                try:

                    while x < len(path):
                        newDict = newDict[camelcaseSnake(path[x])]
                        x += 1
                    newDict['arg'][key] = newDict[key]
                    del newDict[key]
                except:
                    print(traceback.format_exc())
                    print(path)
                    print(newDict)
                    failed = False
            else:
                failed = False
    return fig


def aggregate_value(arg, chart, df):
    key = arg[:-3] + '_agg'
    if 'value' in arg[:5]:
        key = arg.replace('src', '') + '_agg'

    if key in chart:
        aggregation_type = chart[key]
        col = chart[arg]

        if aggregation_type == 'sum':
            aggregated_value = df[col].sum()
        elif aggregation_type == 'average':
            aggregated_value = df[col].mean()
        elif aggregation_type == 'count':
            aggregated_value = df[col].count()
        else:
            raise ValueError("Unsupported aggregation type")

        return aggregated_value

def parseChartKeys_fig(chart, df):
    figureArgs = {}
    realChart = None
    for i, y in getmembers(go, isclass):
        if i.lower() == chart['type'].lower():
            realChart = y
            break
    if realChart:
        chartArgs = getfullargspec(realChart)[0]
        dropping = []
        for arg in figureArgs.keys():
            if arg not in chartArgs and not arg == 'transforms' and not 'src' in arg and not '_agg' in arg:
                dropping.append(arg)
        for i in dropping:
            del figureArgs[i]
        for arg in list(set(chartArgs) | set(chart.keys())):
            try:
                if 'delta' in arg or 'gauge' in arg:
                    rep = 'delta' if 'delta' in arg else 'gauge'
                    if not rep in figureArgs:
                        figureArgs[rep] = chart.get(rep, {})
                    if arg[:-3] + '_agg' in chart:
                        if arg == 'gaugevaluesrcsrc':
                            figureArgs[rep]['threshold'] = {'value': aggregate_value(arg, chart, df)}
                        else:
                            figureArgs[rep][arg.replace('src', '').replace(rep, '')] = aggregate_value(arg, chart, df)
                    elif arg != rep and arg in chart and arg+'src' not in chart and 'src' not in arg and arg not in 'meta':
                        figureArgs[rep][arg[:-3].replace(rep, '')] = df[chart[arg]].tolist()
                    if arg != rep and arg in chart and arg+'src' not in chart and 'src' not in arg and arg not in 'meta':
                        figureArgs[arg] = chart[arg]
                elif arg in chart and arg+'src' not in chart and 'src' not in arg and arg not in 'meta':
                    figureArgs[arg] = chart[arg]
                elif arg+'src' not in chart and arg in chart and arg not in ['meta']:
                    if arg.replace('src', '') + '_agg' in chart:
                        figureArgs[arg.replace('src', '')] = aggregate_value(arg, chart, df)
                    else:
                        figureArgs[arg.replace('src', '')] = df[chart[arg]].tolist()
                    figureArgs[arg] = chart[arg]
            except:
                print(traceback.format_exc())
                pass
        figureArgs['skip_invalid'] = True
        newFig = dropInvalidFigure(realChart, figureArgs, chart['type'].title()).to_plotly_json()
        keepDict = {}
        for k, v in chart.items():
            if 'src' in k or '_agg' in k or 'datasource' in k:
                keepDict[k] = v
        newFig = {**chart, **newFig}
        return newFig

def chartToPython(figure, df):
    try:
        data = json.loads(figure)['data']
        datasource = json.loads(figure).get('datasource', 'data')
        layout = json.loads(figure).get('layout')
    except:
        data = figure['data']
        datasource = figure.get('datasource', 'data')
        layout = figure.get('layout')

    sorts = []
    fig = go.Figure()
    for k in figure['layout']:
        try:
            if 'overlaying' in figure['layout'][k]:
                if not figure['layout'][k]['overlaying']:
                    figure['layout'][k]['overlaying'] = 'free'
        except:
            pass
    fig = dropInvalidLayout(layout, fig)
    if 'template' not in layout:
        fig.update_layout(template='none')
    fig = fig.to_plotly_json()

    try:
        returnstring = ''
        for chart in data:
            dff = df.copy()
            if not 'yaxis' in chart:
                chart['yaxis'] = 'y'
            if not 'xaxis' in chart:
                chart['xaxis'] = 'x'
            if 'ysrc' in chart:
                ysrc = chart['ysrc']
            else:
                ysrc = None
            if 'xsrc' in chart:
                xsrc = chart['xsrc']
            else:
                xsrc = None
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
                    dff2 = dff.copy()
                    for grp in groups:
                        returnstring, dff2, sorts = parseTransforms(chart['transforms'], returnstring, ysrc, xsrc, dff2)

                        dff2.reset_index()
                        # if sorts:
                        #     newSort = []
                        #     order = []
                        #     for sort in sorts:
                        #         if 'targetsrc' in sort:
                        #             newSort.append(sort['targetsrc'])
                        #         else:
                        #             newSort.append(xsrc)
                        #         if 'order' in sort:
                        #             if sort['order'] == 'descending':
                        #                 order.append(False)
                        #             else:
                        #                 order.append(True)
                        #         else:
                        #             order.append(True)
                        #     if newSort:
                        #         dff2 = dff2.sort_values(by=newSort, ascending=order)

                        for t in chart['transforms']:
                            if 'groupssrc' in t:
                                if 'enabled' in t:
                                    if t['enabled']:
                                        if t['type'] == 'groupby':
                                            t['groups'] = dff2[t['groupssrc']].tolist()
                                            t['styles'] = [{x: {}} for x in dff2[t['groupssrc']].unique().tolist()]
                                else:
                                    if t['type'] == 'groupby' and t['groupssrc']:
                                        t['groups'] = dff2[t['groupssrc']].tolist()
                                        t['styles'] = [{x: {}} for x in dff2[t['groupssrc']].unique().tolist()]
                        newchart = parseChartKeys_fig(chart, dff2)
                        # if x['value']:
                        #     if 'name' not in x['value']:
                        #         x['value']['name'] = x['target']
                        #     newchart = parseChartKeys_fig(chart, dff2, x['value'])
                        # else:
                        #     newchart = parseChartKeys_fig(chart, dff2, {'name': x['target']})
                        newchart['transforms'] = chart['transforms']
                        fig['data'].append(newchart)
                        # fig.add_trace(newchart)
                else:
                    returnstring, dff, sorts = parseTransforms(chart['transforms'], returnstring, ysrc, xsrc, dff)

                    # if sorts:
                    #     newSort = []
                    #     order = []
                    #     for sort in sorts:
                    #         if 'targetsrc' in sort:
                    #             newSort.append(sort['targetsrc'])
                    #         else:
                    #             newSort.append(xsrc)
                    #         if 'order' in sort:
                    #             if sort['order'] == 'descending':
                    #                 order.append(False)
                    #             else:
                    #                 order.append(True)
                    #         else:
                    #             order.append(True)
                    #     if newSort:
                    #         dff = dff.sort_values(by=newSort, ascending=order)

                    newchart = parseChartKeys_fig(chart, dff)
                    fig['data'].append(newchart)

            else:
                newchart = parseChartKeys_fig(chart, dff)
                fig['data'].append(newchart)
        fig['datasource'] = datasource
    except:
        print(traceback.format_exc())
    return fig

def cleanDataFromFigure(figure):
    cleaning = ['x', 'y', 'z', 'values', 'meta', 'labels', 'locations', 'lat', 'lon',
                'open', 'close', 'low', 'high',
                'target', 'groups', 'styles']
    special = ['indicator']
    spec_cleaning = ['valuesrc', 'value', 'deltasrc', 'deltareferencesrc', 'gaugesrc', 'gaugevaluesrc']
    for d in figure['data']:
        for k in cleaning:
            if k in d.keys():
                del d[k]
        if d['type'] in special:
            for k in spec_cleaning:
                if k in d.keys():
                    del d[k]
        if 'transforms' in d:
            for t in d['transforms']:
                for k in cleaning:
                    if k in t.keys():
                        del t[k]
                if t['type'] == 'filter':
                    t['type'] = 'filter_python'
    layout = figure['layout']
    xaxis = layout.get('xaxis', {})
    if xaxis.get('autorange'):
        xaxis.pop('range', None)  # Use pop with default to avoid KeyError

    # Check if 'yaxis' exists in layout and handle potential KeyError
    yaxis = layout.get('yaxis', {})
    if yaxis.get('autorange'):
        yaxis.pop('range', None)
    return figure