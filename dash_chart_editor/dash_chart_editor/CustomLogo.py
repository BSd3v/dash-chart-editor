# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CustomLogo(Component):
    """A CustomLogo component.


Keyword arguments:

- src (string; optional)

- style (dict; default {'width':'100%', 'height': '50px', 'margin': '0px'})"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_chart_editor'
    _type = 'CustomLogo'
    @_explicitize_args
    def __init__(self, src=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ['src', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['src', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(CustomLogo, self).__init__(**args)
