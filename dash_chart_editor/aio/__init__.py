"""
Dash All-In-One (AIO) Components for chart editing.
"""

from .chart_editor_aio import ChartEditorAIO
from .multi_chart_editor_aio import MultiChartEditorAIO

try:
    from .models import ChartConfigModel, MultiChartConfigModel
    from .pydantic_chart_editor import PydanticChartEditor, create_pydantic_chart_editor_app
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

__all__ = [
    'ChartEditorAIO',
    'MultiChartEditorAIO',
]

if PYDANTIC_AVAILABLE:
    __all__.extend(['ChartConfigModel', 'MultiChartConfigModel', 'PydanticChartEditor', 'create_pydantic_chart_editor_app'])
