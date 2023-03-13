# AUTO GENERATED FILE - DO NOT EDIT

export ''_charteditor

"""
    ''_charteditor(;kwargs...)
    ''_charteditor(children::Any;kwargs...)
    ''_charteditor(children_maker::Function;kwargs...)


A ChartEditor component.

Keyword arguments:
- `children` (a list of or a singular dash component, string or number; optional)
- `annotateOptions` (optional): . annotateOptions has the following type: Bool | lists containing elements 'text', 'shapes', 'images'.
Those elements have the following types:
  - `text` (Bool; optional)
  - `shapes` (Bool; optional)
  - `images` (Bool; optional)
- `controlOptions` (optional): . controlOptions has the following type: Bool | lists containing elements 'sliders', 'menus'.
Those elements have the following types:
  - `sliders` (Bool; optional)
  - `menus` (Bool; optional)
- `logoSrc` (String; optional)
- `logoStyle` (Dict; optional)
- `menuPanelOrder` (Array; optional)
- `structureOptions` (optional): . structureOptions has the following type: Bool | lists containing elements 'traces', 'subplots', 'transforms'.
Those elements have the following types:
  - `traces` (Bool; optional)
  - `subplots` (Bool; optional)
  - `transforms` (Bool; optional)
- `styleOptions` (optional): . styleOptions has the following type: Bool | lists containing elements 'general', 'traces', 'axes', 'maps', 'legend', 'colorBars'.
Those elements have the following types:
  - `general` (Bool; optional)
  - `traces` (Bool; optional)
  - `axes` (Bool; optional)
  - `maps` (Bool; optional)
  - `legend` (Bool; optional)
  - `colorBars` (Bool; optional)
"""
function ''_charteditor(; kwargs...)
        available_props = Symbol[:children, :annotateOptions, :controlOptions, :logoSrc, :logoStyle, :menuPanelOrder, :structureOptions, :styleOptions]
        wild_props = Symbol[]
        return Component("''_charteditor", "ChartEditor", "dash_chart_editor", available_props, wild_props; kwargs...)
end

''_charteditor(children::Any; kwargs...) = ''_charteditor(;kwargs..., children = children)
''_charteditor(children_maker::Function; kwargs...) = ''_charteditor(children_maker(); kwargs...)

