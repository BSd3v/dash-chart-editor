# AUTO GENERATED FILE - DO NOT EDIT

export ''_dashcharteditor

"""
    ''_dashcharteditor(;kwargs...)

A DashChartEditor component.

Keyword arguments:
- `id` (String; optional): Dash prop to be registered for use with callbacks
- `annotateOptions` (optional): Options that drive the available options under the "Annotate" tree. annotateOptions has the following type: Bool | lists containing elements 'text', 'shapes', 'images'.
Those elements have the following types:
  - `text` (Bool; optional)
  - `shapes` (Bool; optional)
  - `images` (Bool; optional)
- `config` (Dict; optional): Plotly config options, listed here: https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
- `controlOptions` (optional): Options that drive the available options under the "Control" tree. controlOptions has the following type: Bool | lists containing elements 'sliders', 'menus'.
Those elements have the following types:
  - `sliders` (Bool; optional)
  - `menus` (Bool; optional)
- `data` (Bool | Real | String | Dict | Array; optional): Output data of the chart editor
- `dataSources` (Dict with Strings as keys and values of type Array; optional): Input dataSources for driving the chart editors selections
- `frames` (Bool | Real | String | Dict | Array; optional): Output frames of the chart editor
- `layout` (Bool | Real | String | Dict | Array; optional): Output layout of the chart editor
- `loadFigure` (Dict with Strings as keys and values of type Bool | Real | String | Dict | Array; optional): {data, layout, frames} given to the chart, used to populate selections and chart when loading
- `logoSrc` (String; optional): Logo that will be displayed in the chart editor
- `logoStyle` (Dict; optional): Style object of the Logo
- `structureOptions` (optional): Options that drive the available options under the "Structure" tree. structureOptions has the following type: Bool | lists containing elements 'traces', 'subplots', 'transforms'.
Those elements have the following types:
  - `traces` (Bool; optional)
  - `subplots` (Bool; optional)
  - `transforms` (Bool; optional)
- `style` (Dict; optional): style of the whole editing element, including charting area
- `styleOptions` (optional): Options that drive the available options under the "Style" tree. styleOptions has the following type: Bool | lists containing elements 'general', 'traces', 'axes', 'maps', 'legend', 'colorBars'.
Those elements have the following types:
  - `general` (Bool; optional)
  - `traces` (Bool; optional)
  - `axes` (Bool; optional)
  - `maps` (Bool; optional)
  - `legend` (Bool; optional)
  - `colorBars` (Bool; optional)
- `traceOptions` (Bool | Real | String | Dict | Array; optional): List of trace options to display
"""
function ''_dashcharteditor(; kwargs...)
        available_props = Symbol[:id, :annotateOptions, :config, :controlOptions, :data, :dataSources, :frames, :layout, :loadFigure, :logoSrc, :logoStyle, :structureOptions, :style, :styleOptions, :traceOptions]
        wild_props = Symbol[]
        return Component("''_dashcharteditor", "DashChartEditor", "dash_chart_editor", available_props, wild_props; kwargs...)
end

