# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashChartEditor(Component):
    """A DashChartEditor component.


Keyword arguments:

- id (string; optional):
    Dash prop to be registered for use with callbacks.

- annotateOptions (dict; default True):
    Options that drive the available options under the \"Annotate\"
    tree.

    `annotateOptions` is a boolean | dict with keys:

    - images (boolean; optional)

    - shapes (boolean; optional)

    - text (boolean; optional)

- config (dict; default {editable: True}):
    Plotly config options, listed here:
    https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js.

- controlOptions (dict; default True):
    Options that drive the available options under the \"Control\"
    tree.

    `controlOptions` is a boolean | dict with keys:

    - menus (boolean; optional)

    - sliders (boolean; optional)

- data (list of dicts; optional):
    Output data of the chart editor.

- dataSources (dict with strings as keys and values of type list; optional):
    Input dataSources for driving the chart editors selections.

- figure (dict; optional):
    Output figure of the chart editor (dcc.Graph esk output).

    `figure` is a dict with keys:

    - data (list of dicts; optional)

    - frames (list; optional)

    - layout (dict; optional)

- frames (list; optional):
    Output frames of the chart editor.

- layout (dict; optional):
    Output layout of the chart editor.

- loadFigure (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    {data, layout, frames} given to the chart, used to populate
    selections and chart when loading.

- logoSrc (string; optional):
    Logo that will be displayed in the chart editor.

- logoStyle (dict; optional):
    Style object of the Logo.

- structureOptions (dict; default True):
    Options that drive the available options under the \"Structure\"
    tree.

    `structureOptions` is a boolean | dict with keys:

    - subplots (boolean; optional)

    - traces (boolean; optional)

    - transforms (boolean; optional)

- style (dict; default {width: '100%', height: '100%'}):
    style of the whole editing element, including charting area.

- styleOptions (dict; default True):
    Options that drive the available options under the \"Style\" tree.

    `styleOptions` is a boolean | dict with keys:

    - axes (boolean; optional)

    - colorBars (boolean; optional)

    - general (boolean; optional)

    - legend (boolean; optional)

    - maps (boolean; optional)

    - traces (boolean; optional)

- traceOptions (boolean | number | string | dict | list; optional):
    List of trace options to display."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_chart_editor'
    _type = 'DashChartEditor'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, dataSources=Component.UNDEFINED, data=Component.UNDEFINED, layout=Component.UNDEFINED, frames=Component.UNDEFINED, figure=Component.UNDEFINED, style=Component.UNDEFINED, config=Component.UNDEFINED, loadFigure=Component.UNDEFINED, logoSrc=Component.UNDEFINED, logoStyle=Component.UNDEFINED, structureOptions=Component.UNDEFINED, styleOptions=Component.UNDEFINED, annotateOptions=Component.UNDEFINED, controlOptions=Component.UNDEFINED, traceOptions=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'annotateOptions', 'config', 'controlOptions', 'data', 'dataSources', 'figure', 'frames', 'layout', 'loadFigure', 'logoSrc', 'logoStyle', 'structureOptions', 'style', 'styleOptions', 'traceOptions']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'annotateOptions', 'config', 'controlOptions', 'data', 'dataSources', 'figure', 'frames', 'layout', 'loadFigure', 'logoSrc', 'logoStyle', 'structureOptions', 'style', 'styleOptions', 'traceOptions']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashChartEditor, self).__init__(**args)
