"""
Tests for ChartEditorAIO component
"""

import unittest
import pandas as pd
import plotly.express as px
from dash import Dash, html

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_chart_editor.aio import ChartEditorAIO


class TestChartEditorAIO(unittest.TestCase):
    """Test cases for ChartEditorAIO component"""
    
    def setUp(self):
        """Set up test data and app"""
        self.iris_df = px.data.iris()
        self.tips_df = px.data.tips()
        self.data_sources = {
            'iris': self.iris_df,
            'tips': self.tips_df
        }
        self.app = Dash(__name__)
    
    def test_component_initialization_dcc(self):
        """Test component initialization with DCC flavor"""
        component = ChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="test-editor",
            flavor="dcc"
        )
        
        self.assertIsInstance(component, html.Div)
        self.assertEqual(component.aio_id, "test-editor")
        self.assertEqual(component.flavor, "dcc")
        self.assertEqual(component.data_sources, self.data_sources)
    
    def test_component_initialization_auto_id(self):
        """Test component initialization with auto-generated ID"""
        component = ChartEditorAIO(
            data_sources=self.data_sources,
            flavor="dcc"
        )
        
        self.assertIsInstance(component, html.Div)
        self.assertIsNotNone(component.aio_id)
        self.assertTrue(len(component.aio_id) > 0)
    
    def test_component_initialization_no_data(self):
        """Test component initialization without data sources"""
        component = ChartEditorAIO(
            aio_id="empty-editor",
            flavor="dcc"
        )
        
        self.assertIsInstance(component, html.Div)
        self.assertEqual(component.data_sources, {})
    
    def test_component_ids_structure(self):
        """Test that component IDs follow the expected structure"""
        aio_id = "test-id"
        
        expected_ids = [
            'container', 'chart_type', 'data_source', 'x_column', 
            'y_column', 'color_column', 'size_column', 'title', 
            'chart', 'figure_data'
        ]
        
        for id_name in expected_ids:
            id_func = getattr(ChartEditorAIO.ids, id_name)
            result = id_func(aio_id)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result['component'], 'ChartEditorAIO')
            self.assertEqual(result['subcomponent'], id_name)
            self.assertEqual(result['aio_id'], aio_id)
    
    def test_chart_types_available(self):
        """Test that all expected chart types are available"""
        expected_types = ['scatter', 'line', 'bar', 'histogram', 'box', 'violin', 'pie', 'heatmap']
        
        available_types = [ct['value'] for ct in ChartEditorAIO.CHART_TYPES]
        
        for chart_type in expected_types:
            self.assertIn(chart_type, available_types)
    
    def test_invalid_flavor_raises_error(self):
        """Test that invalid flavor raises an error"""
        with self.assertRaises(ImportError):
            ChartEditorAIO(
                data_sources=self.data_sources,
                flavor="dmc"  # Should fail if DMC not installed
            )
    
    def test_layout_generation_dcc(self):
        """Test that DCC layout is generated properly"""
        component = ChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="layout-test",
            flavor="dcc"
        )
        
        # Component should have children
        self.assertTrue(hasattr(component, 'children'))
        self.assertIsNotNone(component.children)
        self.assertIsInstance(component.children, list)
        self.assertTrue(len(component.children) > 0)
    
    def test_column_controls_empty_data(self):
        """Test column controls with empty data"""
        component = ChartEditorAIO(
            data_sources={},
            aio_id="empty-test",
            flavor="dcc"
        )
        
        controls = component._build_column_controls([])
        self.assertIsInstance(controls, html.Div)
    
    def test_column_controls_with_data(self):
        """Test column controls with actual columns"""
        component = ChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="data-test",
            flavor="dcc"
        )
        
        test_columns = ['col1', 'col2', 'col3']
        controls = component._build_column_controls(test_columns)
        
        self.assertIsInstance(controls, html.Div)
    
    def test_component_in_app(self):
        """Test that component can be added to a Dash app"""
        component = ChartEditorAIO(
            data_sources=self.data_sources,
            aio_id="app-test",
            flavor="dcc"
        )
        
        self.app.layout = html.Div([component])
        
        # Should not raise any errors
        self.assertIsNotNone(self.app.layout)


if __name__ == '__main__':
    unittest.main()