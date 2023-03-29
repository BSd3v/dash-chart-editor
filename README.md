# Dash Chart Editor

Dash Chart Editor is a Dash component wrapper for the [Plotly React Chart Editor](https://github.com/plotly/react-chart-editor) package, enabling you to use an editor panel for Plotly charts in your Dash app.

### Installation
`pip install dash-chart-editor`

To build locally see the [Contributing Guide](https://github.com/BSd3v/dash-chart-editor/blob/main/CONTRIBUTING.md)


### Demo and Quickstart

![chart-editor-quickstart](https://user-images.githubusercontent.com/72614349/228352185-77700687-764b-424b-9384-83ca87c6050d.gif)



```python
import dash_chart_editor as dce
from dash import Dash, html
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])


app.layout = html.Div([
    html.H4("Dash Chart Editor Demo with the Plotly Solar dataset"),
    dce.DashChartEditor(dataSources=df.to_dict("list")),
])


if __name__ == "__main__":
    app.run_server(debug=True)

```

### Examples

See more demo apps in the `/examples` folder

- [quickstart.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/quickstart.py)  The quickstart app shown above.    

- [figure_templates.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/figure_templates.py) - A demo on how to use plotly figure templates with the chart editor.   

- [figure_templates_dbc.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/figure_templates_dbc.py) -  A demo of Bootstrap themed figure templates from the [Dash Bootstrap Templates](https://github.com/AnnMarieW/dash-bootstrap-templates) library.    

- [customize.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/customize.py) - Example of ways to customize DashChartEditor
  - add a logo with `logoSrc`
  - only allow certain figure types with `traceOptions`
  - set graph mode bar menu with `config`.  See all the options https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js.  
  
- [default_figure.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/default_figure.py) - Shows how to add a default figure to use when the app starts.
 

- [change_datasets.py](https://github.com/BSd3v/dash-chart-editor/blob/dev/examples/change_datasets.py) - An example showing loading different datasets in a dropdown

- [display_dce_figure_in_dccGraph.py]() - This app shows how to save a figure edited in `dash-chart-editor` and using
it in a different part of a dashboard - in this case it's displayed in a `dcc.Graph()`.

- [three_figure_demo.py]() - This demos how to use a dash-chart-editor in a model to update three different figures in an app.

### Contributing

We welcome contributions to dash-chart-editor. If you find a bug or something is unclear please submit a bug report, if you have ideas for new features please feel free to make a feature request.

If you would like to submit a pull request, please read our [contributing guide](https://github.com/BSd3v/dash-chart-editor/blob/dev/CONTRIBUTING.md), which contains instructions on how to build and install dash-chart-editor locally, and how to submit the pull request itself.

### Dash Chart Editor Reference

Access this documentation in your Python terminal with:
```
>>> import dash_chart_editor
>>> help(dash_chart_editor.DashChartEditor)

```

```   
- id (string; optional):
    Dash prop to be registered for use with callbacks.
   
- annotateOptions (dict; default True):
    Options that drive the available options under the "Annotate"
    tree.
   
    `annotateOptions` is a boolean | dict with keys:
   
    - images (boolean; optional)
   
    - shapes (boolean; optional)
   
    - text (boolean; optional)
   
- config (dict; default {editable: True}):
    Plotly config options, listed here:
    https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js.
   
- controlOptions (dict; default True):
    Options that drive the available options under the "Control"
    tree.
   
    `controlOptions` is a boolean | dict with keys:
   
    - menus (boolean; optional)
   
    - sliders (boolean; optional)
   
- data (boolean | number | string | dict | list; optional):
    Output data of the chart editor.
   
- dataSources (dict with strings as keys and values of type list; optional):
    Input dataSources for driving the chart editors selections.
 
- figure (dict; optional):
     Output figure of the chart editor (dcc.Graph esk output).

- frames (boolean | number | string | dict | list; optional):
    Output frames of the chart editor.
   
- layout (boolean | number | string | dict | list; optional):
    Output layout of the chart editor.
   
- loadFigure (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    {data, layout, frames} given to the chart, used to populate
    selections and chart when loading.
   
- logoSrc (string; optional):
    Logo that will be displayed in the chart editor.
   
- logoStyle (dict; optional):
    Style object of the Logo.
    
- saveState (boolean; default True):
     When passed True, this will save the current state of the grid to `figure`.
 
   
- structureOptions (dict; default True):
    Options that drive the available options under the "Structure"
    tree.
   
    `structureOptions` is a boolean | dict with keys:
   
    - subplots (boolean; optional)
   
    - traces (boolean; optional)
   
    - transforms (boolean; optional)
   
- style (dict; default {width: '100%', height: '100%'}):
    style of the whole editing element, including charting area.
   
- styleOptions (dict; default True):
    Options that drive the available options under the "Style" tree.
   
    `styleOptions` is a boolean | dict with keys:
   
    - axes (boolean; optional)
   
    - colorBars (boolean; optional)
   
    - general (boolean; optional)
   
    - legend (boolean; optional)
   
    - maps (boolean; optional)
   
    - traces (boolean; optional)
   
- traceOptions (boolean | number | string | dict | list; optional):
    List of trace options to display.
 ``` 




