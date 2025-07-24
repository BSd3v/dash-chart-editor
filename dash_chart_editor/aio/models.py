"""
Pydantic models for chart configuration in AIO components.

These models define the structure and validation for chart configuration
forms used with dash-pydantic-form.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class ChartConfigModel(BaseModel):
    """
    Pydantic model for chart configuration.
    
    This model defines all the configurable properties for creating charts
    and is used to auto-generate forms using dash-pydantic-form.
    """
    
    chart_type: Literal[
        'scatter', 'line', 'bar', 'histogram', 
        'box', 'violin', 'pie', 'heatmap'
    ] = Field(
        default='scatter',
        title="Chart Type",
        description="Select the type of chart to create"
    )
    
    data_source: Optional[str] = Field(
        default=None,
        title="Data Source",
        description="Select the dataset to use for the chart"
    )
    
    x_column: Optional[str] = Field(
        default=None,
        title="X-Axis Column",
        description="Select the column to use for the X-axis"
    )
    
    y_column: Optional[str] = Field(
        default=None,
        title="Y-Axis Column", 
        description="Select the column to use for the Y-axis"
    )
    
    color_column: Optional[str] = Field(
        default=None,
        title="Color Column",
        description="Select a column for color mapping (optional)"
    )
    
    size_column: Optional[str] = Field(
        default=None,
        title="Size Column",
        description="Select a column for size mapping (optional)"
    )
    
    title: str = Field(
        default="Chart Title",
        title="Chart Title",
        description="Enter a title for the chart"
    )


class MultiChartConfigModel(BaseModel):
    """
    Pydantic model for multi-chart configuration.
    
    This model manages configuration for multiple charts including
    layout and individual chart selection.
    """
    
    layout_mode: Literal[
        'single', 'grid_2x2', 'grid_3x3', 'vertical', 'horizontal'
    ] = Field(
        default='single',
        title="Layout Mode",
        description="Choose how to display multiple charts"
    )
    
    selected_chart_index: int = Field(
        default=0,
        title="Selected Chart",
        description="Index of the currently selected chart for editing",
        ge=0
    )


# Chart type choices for reference
CHART_TYPES = [
    {'label': 'Scatter Plot', 'value': 'scatter'},
    {'label': 'Line Chart', 'value': 'line'},
    {'label': 'Bar Chart', 'value': 'bar'},
    {'label': 'Histogram', 'value': 'histogram'},
    {'label': 'Box Plot', 'value': 'box'},
    {'label': 'Violin Plot', 'value': 'violin'},
    {'label': 'Pie Chart', 'value': 'pie'},
    {'label': 'Heatmap', 'value': 'heatmap'}
]

# Layout mode choices for reference
LAYOUT_MODES = [
    {'label': 'Single Chart View', 'value': 'single'},
    {'label': 'Grid View (2x2)', 'value': 'grid_2x2'},
    {'label': 'Grid View (3x3)', 'value': 'grid_3x3'},
    {'label': 'Vertical Layout', 'value': 'vertical'},
    {'label': 'Horizontal Layout', 'value': 'horizontal'}
]