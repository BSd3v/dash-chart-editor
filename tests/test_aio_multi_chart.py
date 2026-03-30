"""
Tests for MultiChartEditorAIO component
"""

import unittest
import pandas as pd
import plotly.express as px
from dash import Dash, html

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_chart_editor.aio import MultiChartEditorAIO


class TestMultiChartEditorAIO(unittest.TestCase):
    """Test cases for MultiChartEditorAIO component"""
    
    def setUp(self):
        """Set up test data and app"""
        self.iris_df = px.data.iris()
        self.tips_df = px.data.tips()
        self.data_sources = {
            'iris': self.iris_df,
            'tips': self.tips_df
        }
        self.app = Dash(__name__)
    
    def test_component_initialization_pydantic(self):
        """Test component initialization with pydantic-form flavor"""
        component = MultiChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="test-multi-editor",
            flavor="pydantic_form"
        )
        
        self.assertIsInstance(component, html.Div)
        self.assertEqual(component.aio_id, "test-multi-editor")
        self.assertEqual(component.flavor, "pydantic_form")
        self.assertEqual(component.data_sources, self.data_sources)
    
    def test_component_initialization_auto_id(self):
        """Test component initialization with auto-generated ID"""
        component = MultiChartEditorAIO(
            data_sources=self.data_sources,
            flavor="pydantic_form"
        )
        
        self.assertIsInstance(component, html.Div)
        self.assertIsNotNone(component.aio_id)
        self.assertTrue(len(component.aio_id) > 0)
    
    def test_component_ids_structure(self):
        """Test that component IDs follow the expected structure"""
        aio_id = "test-multi-id"
        
        expected_ids = [
            'container', 'chart_list', 'selected_chart', 'add_chart_btn',
            'remove_chart_btn', 'chart_editor_container', 'charts_display',
            'layout_mode', 'charts_data'
        ]
        
        for id_name in expected_ids:
            id_func = getattr(MultiChartEditorAIO.ids, id_name)
            result = id_func(aio_id)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result['component'], 'MultiChartEditorAIO')
            self.assertEqual(result['subcomponent'], id_name)
            self.assertEqual(result['aio_id'], aio_id)
    
    def test_layout_modes_available(self):
        """Test that all expected layout modes are available"""
        expected_modes = ['single', 'grid_2x2', 'grid_1x3', 'grid_3x1']
        
        available_modes = [lm['value'] for lm in MultiChartEditorAIO.LAYOUT_MODES]
        
        for mode in expected_modes:
            self.assertIn(mode, available_modes)
    
    def test_layout_generation(self):
        """Test that layout is generated properly"""
        component = MultiChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="multi-layout-test",
            flavor="pydantic_form"
        )
        
        # Component should have children
        self.assertTrue(hasattr(component, 'children'))
        self.assertIsNotNone(component.children)
        self.assertIsInstance(component.children, list)
        self.assertTrue(len(component.children) > 0)
    
    def test_component_in_app(self):
        """Test that component can be added to a Dash app"""
        component = MultiChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="multi-app-test",
            flavor="pydantic_form"
        )
        
        self.app.layout = html.Div([component])
        
        # Should not raise any errors
        self.assertIsNotNone(self.app.layout)
    
    def test_invalid_flavor_raises_error(self):
        """Test that invalid flavor raises an error"""
        with self.assertRaises(ValueError):
            MultiChartEditorAIO(
                data_sources=self.data_sources,
                flavor="not-supported"
            )


class TestAIOIntegration(unittest.TestCase):
    """Test integration between AIO components"""
    
    def setUp(self):
        """Set up test data"""
        self.iris_df = px.data.iris()
        self.data_sources = {'iris': self.iris_df}
    
    def test_both_components_in_same_app(self):
        """Test that both AIO components can coexist in the same app"""
        from dash_chart_editor.aio import ChartEditorAIO, MultiChartEditorAIO
        
        app = Dash(__name__)
        
        single_editor = ChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="single",
            flavor="pydantic_form"
        )
        
        multi_editor = MultiChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="multi",
            flavor="pydantic_form"
        )
        
        app.layout = html.Div([
            html.H1("Integration Test"),
            single_editor,
            html.Hr(),
            multi_editor
        ])
        
        # Should not raise any errors
        self.assertIsNotNone(app.layout)
    
    def test_unique_ids_across_components(self):
        """Test that different components have unique IDs"""
        from dash_chart_editor.aio import ChartEditorAIO, MultiChartEditorAIO
        
        aio_id = "same-id"
        
        single_id = ChartEditorAIO.ids.chart(aio_id)
        multi_id = MultiChartEditorAIO.ids.charts_display(aio_id)
        
        # Should be different components
        self.assertNotEqual(single_id['component'], multi_id['component'])


if __name__ == '__main__':
    unittest.main()
