"""
Test separate chart editor components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.express as px
from dash_chart_editor.aio.dcc_chart_editor import DCCChartEditor
from dash_chart_editor.aio import PYDANTIC_AVAILABLE

def test_dcc_chart_editor():
    """Test that DCCChartEditor can be instantiated"""
    # Sample data
    iris_df = px.data.iris()
    data_sources = {'Iris': iris_df}
    
    # Create component
    editor = DCCChartEditor(
        data_sources=data_sources,
        component_id="test-dcc"
    )
    
    assert editor is not None
    assert editor.component_id == "test-dcc"
    assert len(editor.data_sources) == 1
    print("✓ DCCChartEditor instantiation test passed")

def test_pydantic_chart_editor():
    """Test that PydanticChartEditor can be instantiated if available"""
    if not PYDANTIC_AVAILABLE:
        print("✗ PydanticChartEditor not available (dash-pydantic-form not installed)")
        return
    
    from dash_chart_editor.aio.pydantic_chart_editor import PydanticChartEditor
    
    # Sample data
    iris_df = px.data.iris()
    data_sources = {'Iris': iris_df}
    
    # Create component
    editor = PydanticChartEditor(
        data_sources=data_sources,
        component_id="test-pydantic"
    )
    
    assert editor is not None
    assert editor.component_id == "test-pydantic"
    assert len(editor.data_sources) == 1
    print("✓ PydanticChartEditor instantiation test passed")

def test_separate_components():
    """Test that both components can be instantiated separately"""
    test_dcc_chart_editor()
    test_pydantic_chart_editor()
    print("✓ Both chart editor components work independently")

if __name__ == "__main__":
    test_separate_components()
    print("All tests passed!")