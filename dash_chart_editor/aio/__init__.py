"""
Dash All-In-One (AIO) Components for Chart Editing

This module provides native Dash components as an alternative to the react-chart-editor.
It includes both AIO components and standalone chart editors with different flavors.
"""

from .chart_editor_aio import ChartEditorAIO
from .multi_chart_editor_aio import MultiChartEditorAIO

# Standalone chart editor components (separate from AIO pattern)
from .dcc_chart_editor import DCCChartEditor, create_dcc_chart_editor_app

try:
    from .models import ChartConfigModel, MultiChartConfigModel
    from .pydantic_chart_editor import PydanticChartEditor, create_pydantic_chart_editor_app
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

__all__ = [
    'ChartEditorAIO',
    'MultiChartEditorAIO', 
    'DCCChartEditor',
    'create_dcc_chart_editor_app'
]

if PYDANTIC_AVAILABLE:
    __all__.extend(['ChartConfigModel', 'MultiChartConfigModel', 'PydanticChartEditor', 'create_pydantic_chart_editor_app'])