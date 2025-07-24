# AIO Components Documentation

## Overview

This document provides comprehensive guidance for using the new Dash All-In-One (AIO) components as an alternative to the react-chart-editor. The AIO components provide native Dash-based chart editing capabilities with improved integration into the Dash ecosystem.

## Components

### ChartEditorAIO

A single chart editor component that provides an interface for creating and editing individual charts using native Dash components.

#### Features
- Support for 8 chart types: scatter, line, bar, histogram, box, violin, pie, heatmap
- Dynamic data source and column selection
- Real-time chart updates via native Dash callbacks
- Support for both DCC and DMC (Dash Mantine Components) UI flavors
- Configurable styling and layout options

#### Basic Usage

```python
from dash_chart_editor.aio import ChartEditorAIO
import pandas as pd
import plotly.express as px

# Prepare your data
iris_df = px.data.iris()
tips_df = px.data.tips()

data_sources = {
    'Iris Dataset': iris_df,
    'Tips Dataset': tips_df
}

# Create the component
chart_editor = ChartEditorAIO(
    data_sources=data_sources,
    aio_id="my-editor",
    flavor="dcc"  # or "dmc" for Dash Mantine Components
)
```

#### Parameters

- **data_sources** (Dict[str, pd.DataFrame]): Dictionary of dataframes with names as keys
- **aio_id** (str, optional): Unique identifier for this AIO instance. Auto-generated if not provided.
- **flavor** (str): UI flavor - 'dcc' or 'dmc'. Default is 'dcc'.
- **kwargs**: Additional properties passed to the container div

#### Component IDs

The component exposes the following IDs for external callback integration:

```python
ChartEditorAIO.ids.chart_type(aio_id)     # Chart type dropdown
ChartEditorAIO.ids.data_source(aio_id)    # Data source dropdown
ChartEditorAIO.ids.x_column(aio_id)       # X column dropdown
ChartEditorAIO.ids.y_column(aio_id)       # Y column dropdown
ChartEditorAIO.ids.color_column(aio_id)   # Color column dropdown
ChartEditorAIO.ids.size_column(aio_id)    # Size column dropdown
ChartEditorAIO.ids.title(aio_id)          # Chart title input
ChartEditorAIO.ids.chart(aio_id)          # Chart display
ChartEditorAIO.ids.figure_data(aio_id)    # Hidden div storing figure data
```

### MultiChartEditorAIO

A multi-chart management component that allows creating, editing, and managing multiple charts with different layout modes.

#### Features
- Create and manage multiple charts
- Switch between charts for editing
- Multiple display modes: single view, 2x2 grid, 1x3 grid, 3x1 grid
- Chart management (add/remove charts)
- Integration with ChartEditorAIO for individual chart editing

#### Basic Usage

```python
from dash_chart_editor.aio import MultiChartEditorAIO

multi_editor = MultiChartEditorAIO(
    data_sources=data_sources,
    aio_id="multi-editor",
    flavor="dcc"
)
```

#### Parameters

Same as ChartEditorAIO.

#### Component IDs

```python
MultiChartEditorAIO.ids.chart_list(aio_id)           # Chart list dropdown
MultiChartEditorAIO.ids.selected_chart(aio_id)       # Selected chart dropdown
MultiChartEditorAIO.ids.add_chart_btn(aio_id)        # Add chart button
MultiChartEditorAIO.ids.remove_chart_btn(aio_id)     # Remove chart button
MultiChartEditorAIO.ids.layout_mode(aio_id)          # Layout mode dropdown
MultiChartEditorAIO.ids.charts_display(aio_id)       # Charts display area
MultiChartEditorAIO.ids.charts_data(aio_id)          # Hidden storage for charts data
```

## Examples

### Example 1: Single Chart Editor (DCC Flavor)

See `examples/aio_single_chart.py` for a complete example demonstrating:
- Single chart editing with DCC components
- Dynamic data source and column selection
- Real-time chart updates
- Support for all chart types

### Example 2: Multi-Chart Editor

See `examples/aio_multi_chart.py` for an example showing:
- Multiple chart creation and management
- Chart selection and editing
- Different layout modes for chart display

### Example 3: DMC Flavor

See `examples/aio_dmc_flavor.py` for an example using:
- Dash Mantine Components for a modern UI
- Same functionality as DCC flavor with improved styling

## Integration with Existing Applications

### Using with Custom Callbacks

You can integrate the AIO components with your existing callbacks by referencing their IDs:

```python
from dash import Input, Output, callback

@callback(
    Output("my-output", "children"),
    Input(ChartEditorAIO.ids.figure_data("my-editor"), "children")
)
def handle_chart_updates(figure_data):
    # Process the figure data
    return f"Chart updated: {figure_data}"
```

### Data Management

For the components to work with your data, you need to implement callbacks that:

1. Update column options when data source changes
2. Update charts when selections change
3. Handle data conversion between stored format and DataFrames

Example pattern:

```python
@callback(
    Output(f"column-controls-{aio_id}", "children"),
    Input(ChartEditorAIO.ids.data_source(aio_id), "value"),
    State("data-store", "data")
)
def update_column_options(data_source, stored_data):
    if not data_source or data_source not in stored_data:
        return "Select a data source to see column options."
    
    df = pd.DataFrame(stored_data[data_source])
    columns = df.columns.tolist()
    # Build column selection controls...
```

## Migration from react-chart-editor

### Key Differences

| react-chart-editor | AIO Components |
|-------------------|----------------|
| React-based component | Native Dash components |
| Single monolithic component | Modular AIO components |
| Limited customization | Full Dash callback integration |
| External dependency | Built-in to dash-chart-editor |
| Fixed UI styling | Configurable DCC/DMC flavors |

### Migration Steps

1. **Replace component imports:**
   ```python
   # Old
   from dash_chart_editor import DashChartEditor
   
   # New
   from dash_chart_editor.aio import ChartEditorAIO
   ```

2. **Update component instantiation:**
   ```python
   # Old
   DashChartEditor(
       dataSources=data_sources,
       figure=figure
   )
   
   # New
   ChartEditorAIO(
       data_sources=data_sources,
       aio_id="editor-1",
       flavor="dcc"
   )
   ```

3. **Implement data handling callbacks:**
   The AIO components require custom callbacks for data management, providing more flexibility but requiring additional setup.

4. **Update callback patterns:**
   Replace single component callbacks with AIO-pattern callbacks using the component IDs.

### Backward Compatibility

The original `DashChartEditor` component remains available and unchanged, ensuring existing applications continue to work without modification. The AIO components are provided as an additional option for new development or gradual migration.

## Chart Types Supported

1. **Scatter Plot** (`scatter`): X/Y coordinates with optional color and size mapping
2. **Line Chart** (`line`): Connected data points, ideal for time series
3. **Bar Chart** (`bar`): Categorical data with bar heights representing values
4. **Histogram** (`histogram`): Distribution of numerical data
5. **Box Plot** (`box`): Statistical summary showing quartiles and outliers
6. **Violin Plot** (`violin`): Combination of box plot and density estimation
7. **Pie Chart** (`pie`): Proportional data representation
8. **Heatmap** (`heatmap`): 2D data visualization with color intensity

## UI Flavors

### DCC Flavor (Default)
- Uses standard Dash Core Components
- Bootstrap-compatible styling
- Familiar Dash look and feel
- Minimal dependencies

### DMC Flavor
- Uses Dash Mantine Components
- Modern, clean design
- Enhanced user experience
- Requires `dash-mantine-components` installation

## Advanced Usage

### Custom Styling

Both flavors support custom styling through standard Dash patterns:

```python
chart_editor = ChartEditorAIO(
    data_sources=data_sources,
    aio_id="styled-editor",
    flavor="dcc",
    style={"border": "1px solid #ccc", "padding": "20px"}
)
```

### Multiple Instances

You can use multiple AIO components in the same application:

```python
# Different editors for different datasets
editor1 = ChartEditorAIO(data_sources=sales_data, aio_id="sales-editor")
editor2 = ChartEditorAIO(data_sources=user_data, aio_id="user-editor")
```

### State Management

The components store their state internally, but you can access it through the exposed IDs for persistence or synchronization:

```python
@callback(
    Output("app-state", "data"),
    Input(ChartEditorAIO.ids.figure_data("editor"), "children")
)
def save_state(figure_data):
    return {"last_chart": figure_data}
```

## Troubleshooting

### Common Issues

1. **DMC components not working**: Install `dash-mantine-components`
2. **Column options not updating**: Implement the data source change callback
3. **Charts not rendering**: Check data format and column selection
4. **Callback conflicts**: Ensure unique `aio_id` values

### Performance Considerations

- Use `dcc.Store` for large datasets to avoid repeated data processing
- Implement `prevent_initial_call=True` to avoid unnecessary initial renders
- Consider data pagination for very large datasets

## API Reference

### ChartEditorAIO

```python
class ChartEditorAIO(html.Div):
    def __init__(
        self,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None,
        aio_id: Optional[str] = None,
        flavor: str = 'dcc',
        **kwargs
    )
```

### MultiChartEditorAIO

```python
class MultiChartEditorAIO(html.Div):
    def __init__(
        self,
        data_sources: Optional[Dict[str, Any]] = None,
        aio_id: Optional[str] = None,
        flavor: str = 'dcc',
        **kwargs
    )
```

## Contributing

To contribute to the AIO components:

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for any API changes
4. Ensure backward compatibility with existing components

## Support

For issues and questions:
- Check the examples in the `examples/` directory
- Review the test files for usage patterns
- Open an issue on the project repository