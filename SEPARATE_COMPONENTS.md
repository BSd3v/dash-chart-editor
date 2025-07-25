# Separate Chart Editor Components

## Overview

Following feedback about callback conflicts when using multiple flavors in the same application, the chart editor components have been separated into distinct, standalone implementations. This approach prevents callbacks from "stepping on toes" and provides cleaner separation of concerns.

## Components

### DCCChartEditor - Standard Dash Components

A pure DCC implementation that uses only standard Dash components without external dependencies.

**Features:**
- No external dependencies beyond Dash/Plotly/Pandas
- Clean, familiar DCC interface
- Isolated callback system
- 8 chart types supported
- Lightweight and fast

**Usage:**
```python
from dash_chart_editor.aio import DCCChartEditor
import pandas as pd

# Create component
editor = DCCChartEditor(
    data_sources=data_sources,
    component_id="my-dcc-editor"
)

# Register callbacks (required)
editor.register_callbacks(app)
```

**Example App:**
```python
from dash_chart_editor.aio import create_dcc_chart_editor_app
import plotly.express as px

data_sources = {
    'Iris': px.data.iris(),
    'Tips': px.data.tips()
}

app = create_dcc_chart_editor_app(data_sources, port=8055)
app.run(debug=True)
```

### PydanticChartEditor - Advanced Form-Based

A sophisticated implementation using dash-pydantic-form with dynamic chart-specific parameters.

**Features:**
- Chart-type specific parameter detection
- Auto-generated forms with validation
- Dynamic parameter options based on chart type
- Streamlined form data handling
- Professional UI with dash-mantine-components

**Chart-Specific Parameters:**

| Chart Type | Required | Optional |
|------------|----------|----------|
| Scatter | x, y | color, size, symbol, opacity |
| Line | x, y | color, line_dash, markers |
| Bar | x, y | color, orientation, pattern_shape |
| Histogram | x | color, nbins, marginal |
| Box | y | x, color, notched, points |
| Violin | y | x, color, box, points |
| Pie | names, values | color, hole |
| Heatmap | x, y, z | color_continuous_scale |

**Usage:**
```python
from dash_chart_editor.aio import PydanticChartEditor

# Create component
editor = PydanticChartEditor(
    data_sources=data_sources,
    component_id="my-pydantic-editor"
)

# Register callbacks (required)
editor.register_callbacks(app)
```

**Example App:**
```python
from dash_chart_editor.aio import create_pydantic_chart_editor_app

app = create_pydantic_chart_editor_app(data_sources, port=8054)
app.run(debug=True)
```

## Key Differences from AIO Pattern

### Before (AIO with Flavors)
```python
# Potential callback conflicts
editor1 = ChartEditorAIO(data_sources=data, flavor='dcc', aio_id="editor1")
editor2 = ChartEditorAIO(data_sources=data, flavor='pydantic_form', aio_id="editor2")
```

### After (Separate Components)
```python
# Isolated callback systems
editor1 = DCCChartEditor(data_sources=data, component_id="editor1")
editor2 = PydanticChartEditor(data_sources=data, component_id="editor2")

# Each manages its own callbacks
editor1.register_callbacks(app)
editor2.register_callbacks(app)
```

## Benefits of Separation

1. **No Callback Conflicts**: Each component has its own isolated callback namespace
2. **Purpose-Built**: Each component is optimized for its specific use case
3. **Optional Dependencies**: Choose only the dependencies you need
4. **Easier Debugging**: Isolated component logic makes issues easier to trace
5. **Better Performance**: No conditional logic or unused imports

## Installation

**For DCCChartEditor (minimal):**
```bash
pip install dash plotly pandas
```

**For PydanticChartEditor (full features):**
```bash
pip install dash plotly pandas dash-pydantic-form
```

## Examples

### Running Separate Example Pages

1. **DCC Chart Editor**: 
   ```bash
   python examples/dcc_chart_editor_page.py
   # Open http://localhost:8055
   ```

2. **Pydantic Chart Editor**:
   ```bash
   python examples/pydantic_chart_editor_page.py  
   # Open http://localhost:8054
   ```

### Manual Integration

```python
import dash
from dash import html
from dash_chart_editor.aio import DCCChartEditor, PydanticChartEditor

app = dash.Dash(__name__)

# Create both types in the same app (now possible without conflicts!)
dcc_editor = DCCChartEditor(data_sources=data, component_id="dcc-ed")
pydantic_editor = PydanticChartEditor(data_sources=data, component_id="pyd-ed")

app.layout = html.Div([
    html.H2("DCC Editor"),
    dcc_editor,
    html.Hr(),
    html.H2("Pydantic Editor"), 
    pydantic_editor
])

# Register callbacks for both
dcc_editor.register_callbacks(app)
pydantic_editor.register_callbacks(app)

app.run(debug=True)
```

## Migration Guide

### From AIO Flavors to Separate Components

1. **Update Imports:**
   ```python
   # Old
   from dash_chart_editor.aio import ChartEditorAIO
   
   # New
   from dash_chart_editor.aio import DCCChartEditor, PydanticChartEditor
   ```

2. **Update Component Creation:**
   ```python
   # Old
   editor = ChartEditorAIO(data_sources=data, flavor='dcc', aio_id="editor")
   
   # New  
   editor = DCCChartEditor(data_sources=data, component_id="editor")
   editor.register_callbacks(app)  # Important!
   ```

3. **Component IDs Change:**
   ```python
   # Old AIO pattern
   ChartEditorAIO.ids.chart("my-id")
   
   # New pattern  
   f"chart-{component_id}"  # Direct string IDs
   ```

## Chart Type Detection and Parameters

The PydanticChartEditor automatically detects chart-specific parameters and provides appropriate form controls:

```python
# Example: When "scatter" is selected, form shows:
# - Title (text input)
# - X Column (dropdown with available columns)  
# - Y Column (dropdown with available columns)
# - Color Column (optional dropdown)
# - Size Column (optional dropdown)
# - Symbol (optional dropdown)
# - Opacity (optional slider)

# When "pie" is selected, form shows:
# - Title (text input)
# - Names Column (dropdown)
# - Values Column (dropdown) 
# - Color (optional dropdown)
# - Hole (optional slider for donut charts)
```

This dynamic behavior ensures users only see relevant options for their selected chart type, reducing confusion and improving usability.

## Testing

```bash
# Test both component types
python tests/test_separate_components.py

# Individual component tests  
python -c "from dash_chart_editor.aio import DCCChartEditor; print('DCC OK')"
python -c "from dash_chart_editor.aio import PydanticChartEditor; print('Pydantic OK')"
```

## Legacy AIO Components

The original ChartEditorAIO and MultiChartEditorAIO components remain available for backward compatibility but are not recommended for new projects due to potential callback conflicts when mixing flavors.

For new projects, use the separate DCCChartEditor and PydanticChartEditor components instead.