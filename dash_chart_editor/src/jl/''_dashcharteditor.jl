# AUTO GENERATED FILE - DO NOT EDIT

export ''_dashcharteditor

"""
    ''_dashcharteditor(;kwargs...)
    ''_dashcharteditor(children::Any;kwargs...)
    ''_dashcharteditor(children_maker::Function;kwargs...)


A DashChartEditor component.

Keyword arguments:
- `children` (Bool | Real | String | Dict | Array; optional)
- `id` (String; optional)
- `data` (Bool | Real | String | Dict | Array; optional)
- `dataSources` (Dict with Strings as keys and values of type Array; optional)
- `frames` (Bool | Real | String | Dict | Array; optional)
- `layout` (Bool | Real | String | Dict | Array; optional)
- `loadFigure` (Dict with Strings as keys and values of type Bool | Real | String | Dict | Array; optional)
- `style` (Dict; optional)
"""
function ''_dashcharteditor(; kwargs...)
        available_props = Symbol[:children, :id, :data, :dataSources, :frames, :layout, :loadFigure, :style]
        wild_props = Symbol[]
        return Component("''_dashcharteditor", "DashChartEditor", "dash_chart_editor", available_props, wild_props; kwargs...)
end

''_dashcharteditor(children::Any; kwargs...) = ''_dashcharteditor(;kwargs..., children = children)
''_dashcharteditor(children_maker::Function; kwargs...) = ''_dashcharteditor(children_maker(); kwargs...)

