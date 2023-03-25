# Dash Chart Editor

Dash Chart Editor is a Dash component wrapper for the [Plotly React Chart Editor](https://github.com/plotly/react-chart-editor) package, enabling you to use an editor panel for Plotly charts in your Dash app.

### Installation
`pip install dash-chart-editor`

To build locally see the [Contributing Guide](https://github.com/BSd3v/dash-chart-editor/blob/main/CONTRIBUTING.md)


### Demo and Quickstart


![chart-editor-quickstart](https://user-images.githubusercontent.com/72614349/227724301-e5b23a7b-3f23-423a-bebd-a88ba47dbb7c.gif)



```python
import dash_chart_editor as dce
from dash import Dash, html
import plotly.express as px


app = Dash(__name__, external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

df = px.data.gapminder()

app.layout = html.Div([
    html.H4("Dash Chart Editor Demo with the Plotly Gapminder dataset"),
    dce.DashChartEditor(
        dataSources=df.to_dict("list"),
    )
])


if __name__ == "__main__":
    app.run_server(debug=True)


```

### Examples

See more demo apps in the `/examples` folder

- `quickstarat.py`  The quickstart app shown above
- `figure_templates.py` - A demo on how to use plotly figure templates with the chart editor
- `figure_templates_dbc` -  A demo of Bootstrap themed figure templates from the [Dash Bootstrap Templates](https://github.com/AnnMarieW/dash-bootstrap-templates) library




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




