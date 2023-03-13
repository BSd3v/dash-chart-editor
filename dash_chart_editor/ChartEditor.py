# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ChartEditor(Component):
    """A ChartEditor component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- annotateOptions (dict; optional)

    `annotateOptions` is a boolean | dict with keys:

    - images (boolean; optional)

    - shapes (boolean; optional)

    - text (boolean; optional)

- controlOptions (dict; optional)

    `controlOptions` is a boolean | dict with keys:

    - menus (boolean; optional)

    - sliders (boolean; optional)

- logoSrc (string; optional)

- logoStyle (dict; optional)

- menuPanelOrder (list; optional)

- structureOptions (dict; optional)

    `structureOptions` is a boolean | dict with keys:

    - subplots (boolean; optional)

    - traces (boolean; optional)

    - transforms (boolean; optional)

- styleOptions (dict; optional)

    `styleOptions` is a boolean | dict with keys:

    - axes (boolean; optional)

    - colorBars (boolean; optional)

    - general (boolean; optional)

    - legend (boolean; optional)

    - maps (boolean; optional)

    - traces (boolean; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_chart_editor'
    _type = 'ChartEditor'
    @_explicitize_args
    def __init__(self, children=None, logoSrc=Component.UNDEFINED, logoStyle=Component.UNDEFINED, menuPanelOrder=Component.UNDEFINED, structureOptions=Component.UNDEFINED, styleOptions=Component.UNDEFINED, annotateOptions=Component.UNDEFINED, controlOptions=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'annotateOptions', 'controlOptions', 'logoSrc', 'logoStyle', 'menuPanelOrder', 'structureOptions', 'styleOptions']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'annotateOptions', 'controlOptions', 'logoSrc', 'logoStyle', 'menuPanelOrder', 'structureOptions', 'styleOptions']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ChartEditor, self).__init__(children=children, **args)
