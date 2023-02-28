# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashChartEditor(Component):
    """A DashChartEditor component.


Keyword arguments:

- children (boolean | number | string | dict | list; optional)

- id (string; optional)

- data (boolean | number | string | dict | list; optional)

- dataSources (dict with strings as keys and values of type list; optional)

- frames (boolean | number | string | dict | list; optional)

- layout (boolean | number | string | dict | list; optional)

- loadFigure (dict with strings as keys and values of type boolean | number | string | dict | list; optional)

- style (dict; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_chart_editor'
    _type = 'DashChartEditor'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, data=Component.UNDEFINED, dataSources=Component.UNDEFINED, layout=Component.UNDEFINED, frames=Component.UNDEFINED, style=Component.UNDEFINED, loadFigure=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'data', 'dataSources', 'frames', 'layout', 'loadFigure', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'data', 'dataSources', 'frames', 'layout', 'loadFigure', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DashChartEditor, self).__init__(children=children, **args)
