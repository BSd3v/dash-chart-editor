"""
PydanticChartEditor - Chart Editor using dash-pydantic-form

A standalone chart editor component that uses dash-pydantic-form for
configuration forms with streamlined data handling and chart-specific parameters.
"""

import uuid
from typing import Dict, List, Any, Optional, Union
import json

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    from dash_pydantic_form import ModelForm
    from pydantic import BaseModel, Field, create_model
    PYDANTIC_FORM_AVAILABLE = True
except ImportError:
    PYDANTIC_FORM_AVAILABLE = False


class PydanticChartEditor(html.Div):
    """
    A standalone chart editor using dash-pydantic-form.
    
    This component is separate from the AIO pattern to avoid callback conflicts
    and provides a streamlined approach using pydantic forms.
    """
    
    # Chart type definitions with their specific parameters
    CHART_CONFIGS = {
        'scatter': {
            'required': ['x', 'y'],
            'optional': ['color', 'size', 'symbol', 'opacity'],
            'px_function': 'scatter'
        },
        'line': {
            'required': ['x', 'y'],
            'optional': ['color', 'line_dash', 'markers'],
            'px_function': 'line'
        },
        'bar': {
            'required': ['x', 'y'],
            'optional': ['color', 'orientation', 'pattern_shape'],
            'px_function': 'bar'
        },
        'histogram': {
            'required': ['x'],
            'optional': ['color', 'nbins', 'marginal'],
            'px_function': 'histogram'
        },
        'box': {
            'required': ['y'],
            'optional': ['x', 'color', 'notched', 'points'],
            'px_function': 'box'
        },
        'violin': {
            'required': ['y'],
            'optional': ['x', 'color', 'box', 'points'],
            'px_function': 'violin'
        },
        'pie': {
            'required': ['names', 'values'],
            'optional': ['color', 'hole'],
            'px_function': 'pie'
        },
        'heatmap': {
            'required': ['x', 'y', 'z'],
            'optional': ['color_continuous_scale'],
            'px_function': 'density_heatmap'
        }
    }
    
    def __init__(
        self,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None,
        component_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the PydanticChartEditor component.
        
        Args:
            data_sources: Dictionary of dataframes with names as keys
            component_id: Unique identifier for this component instance
            **kwargs: Additional properties passed to the container
        """
        if not PYDANTIC_FORM_AVAILABLE:
            raise ImportError("dash_pydantic_form is required for PydanticChartEditor")
        
        if component_id is None:
            component_id = str(uuid.uuid4())
        
        self.component_id = component_id
        self.data_sources = data_sources or {}
        
        # Create dynamic models for each chart type
        self.chart_models = self._create_chart_models()
        
        # Build the component
        children = self._build_layout()
        
        super().__init__(
            id=f"pydantic-chart-editor-{component_id}",
            children=children,
            **kwargs
        )
    
    def _create_chart_models(self):
        """Create Pydantic models for each chart type with specific parameters"""
        models = {}
        
        for chart_type, config in self.CHART_CONFIGS.items():
            # Base fields that all charts have
            fields = {
                'chart_type': (str, Field(default=chart_type, title="Chart Type")),
                'data_source': (str, Field(default='', title="Data Source")),
                'title': (str, Field(default='', title="Chart Title")),
            }
            
            # Add required fields
            for param in config['required']:
                fields[param] = (str, Field(default='', title=param.replace('_', ' ').title()))
            
            # Add optional fields
            for param in config['optional']:
                fields[param] = (Optional[str], Field(default=None, title=param.replace('_', ' ').title()))
            
            # Create the model class
            model_name = f"{chart_type.title()}ChartModel"
            models[chart_type] = create_model(model_name, **fields)
        
        return models
    
    def _build_layout(self):
        """Build the layout for the pydantic chart editor"""
        data_source_options = [{'label': name, 'value': name} for name in self.data_sources.keys()]
        
        return [
            html.Div([
                html.H4("Pydantic Chart Editor", style={'marginBottom': '20px'}),
                
                # Chart type selection
                html.Div([
                    html.Label("Chart Type:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id=f"chart-type-{self.component_id}",
                        options=[
                            {'label': chart_type.replace('_', ' ').title(), 'value': chart_type}
                            for chart_type in self.CHART_CONFIGS.keys()
                        ],
                        value='scatter',
                        clearable=False,
                        style={'marginBottom': '15px'}
                    )
                ]),
                
                # Data source selection
                html.Div([
                    html.Label("Data Source:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id=f"data-source-{self.component_id}",
                        options=data_source_options,
                        value=list(self.data_sources.keys())[0] if self.data_sources else None,
                        clearable=False,
                        style={'marginBottom': '15px'}
                    )
                ]),
                
                # Dynamic form container
                html.Div(id=f"dynamic-form-{self.component_id}"),
                
                # Data store for form data
                dcc.Store(id=f"form-data-store-{self.component_id}"),
                
                # Data store for column options
                dcc.Store(id=f"column-options-{self.component_id}"),
                
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}),
            
            # Chart display area
            html.Div([
                dcc.Graph(
                    id=f"chart-{self.component_id}",
                    style={'height': '600px'}
                ),
                # Debug info
                html.Div(id=f"debug-info-{self.component_id}", style={'marginTop': '10px', 'fontSize': '12px', 'color': '#666'})
            ], style={'width': '68%', 'display': 'inline-block', 'marginLeft': '2%'})
        ]
    
    def register_callbacks(self, app):
        """Register callbacks for this component instance"""
        
        # Update column options when data source changes
        @app.callback(
            Output(f"column-options-{self.component_id}", "data"),
            Input(f"data-source-{self.component_id}", "value")
        )
        def update_column_options(data_source):
            if not data_source or data_source not in self.data_sources:
                return []
            
            df = self.data_sources[data_source]
            return df.columns.tolist()
        
        # Update form based on chart type
        @app.callback(
            Output(f"dynamic-form-{self.component_id}", "children"),
            [
                Input(f"chart-type-{self.component_id}", "value"),
                Input(f"column-options-{self.component_id}", "data")
            ]
        )
        def update_dynamic_form(chart_type, columns):
            if not chart_type or not columns:
                return html.Div("Select a chart type and data source to configure parameters.")
            
            # Create form fields based on chart type configuration
            config = self.CHART_CONFIGS[chart_type]
            form_fields = []
            
            # Title field
            form_fields.append(
                html.Div([
                    html.Label("Chart Title:"),
                    dcc.Input(
                        id=f"title-{self.component_id}",
                        type='text',
                        placeholder='Enter chart title...',
                        style={'width': '100%', 'marginBottom': '10px'}
                    )
                ])
            )
            
            # Required fields
            for param in config['required']:
                label = param.replace('_', ' ').title()
                if param in ['names', 'values']:  # Special handling for pie chart
                    if param == 'names':
                        label = "Names Column"
                    elif param == 'values':
                        label = "Values Column"
                
                form_fields.append(
                    html.Div([
                        html.Label(f"{label}:", style={'color': 'red' if param in config['required'] else 'black'}),
                        dcc.Dropdown(
                            id=f"{param}-{self.component_id}",
                            options=[{'label': col, 'value': col} for col in columns],
                            placeholder=f"Select {label.lower()}...",
                            style={'marginBottom': '10px'}
                        )
                    ])
                )
            
            # Optional fields
            for param in config['optional']:
                label = param.replace('_', ' ').title()
                form_fields.append(
                    html.Div([
                        html.Label(f"{label} (optional):"),
                        dcc.Dropdown(
                            id=f"{param}-{self.component_id}",
                            options=[{'label': col, 'value': col} for col in columns],
                            placeholder=f"Select {label.lower()}...",
                            clearable=True,
                            style={'marginBottom': '10px'}
                        )
                    ])
                )
            
            return html.Div(form_fields)
        
        # Update chart based on form inputs
        @app.callback(
            [
                Output(f"chart-{self.component_id}", "figure"),
                Output(f"debug-info-{self.component_id}", "children")
            ],
            [
                Input(f"chart-type-{self.component_id}", "value"),
                Input(f"data-source-{self.component_id}", "value"),
                Input(f"title-{self.component_id}", "value"),
            ] + [
                Input(f"{param}-{self.component_id}", "value")
                for chart_config in self.CHART_CONFIGS.values()
                for param in chart_config['required'] + chart_config['optional']
            ],
            prevent_initial_call=True
        )
        def update_chart(*args):
            # Parse inputs
            chart_type = args[0]
            data_source = args[1]
            title = args[2]
            
            if not chart_type or not data_source or data_source not in self.data_sources:
                fig = go.Figure()
                fig.update_layout(title="Select chart type and data source")
                return fig, "Waiting for inputs..."
            
            # Get the data
            df = self.data_sources[data_source]
            config = self.CHART_CONFIGS[chart_type]
            
            # Parse the parameter values
            param_values = {}
            param_index = 3  # Start after chart_type, data_source, title
            
            for chart_config in self.CHART_CONFIGS.values():
                for param in chart_config['required'] + chart_config['optional']:
                    if param_index < len(args):
                        param_values[param] = args[param_index]
                    param_index += 1
            
            # Build chart parameters for the current chart type
            chart_params = {'data_frame': df}
            
            # Add title
            if title:
                chart_params['title'] = title
            
            # Add required parameters
            for param in config['required']:
                if param in param_values and param_values[param]:
                    chart_params[param] = param_values[param]
                else:
                    fig = go.Figure()
                    fig.update_layout(title=f"Missing required parameter: {param}")
                    return fig, f"Missing required parameter: {param}"
            
            # Add optional parameters
            for param in config['optional']:
                if param in param_values and param_values[param]:
                    chart_params[param] = param_values[param]
            
            # Create the chart
            try:
                px_function = getattr(px, config['px_function'])
                fig = px_function(**chart_params)
                fig.update_layout(height=550)
                
                debug_info = f"Chart: {chart_type}, Params: {list(chart_params.keys())}"
                return fig, debug_info
                
            except Exception as e:
                fig = go.Figure()
                fig.update_layout(title=f"Error creating chart: {str(e)}")
                return fig, f"Error: {str(e)}"


def create_pydantic_chart_editor_app(data_sources: Dict[str, pd.DataFrame], port: int = 8054):
    """
    Create a standalone Dash app with PydanticChartEditor.
    
    Args:
        data_sources: Dictionary of dataframes
        port: Port to run the app on
    
    Returns:
        Dash app instance
    """
    app = dash.Dash(__name__)
    
    # Create the editor component
    editor = PydanticChartEditor(
        data_sources=data_sources,
        component_id="main-editor"
    )
    
    app.layout = html.Div([
        html.Div([
            html.H1("Pydantic Chart Editor", 
                   style={'textAlign': 'center', 'marginBottom': '10px'}),
            html.P("Chart editor using dash-pydantic-form with dynamic chart-specific parameters.", 
                  style={'textAlign': 'center', 'color': '#666', 'fontSize': '18px', 'marginBottom': '30px'})
        ], style={'backgroundColor': '#f8f9fa', 'padding': '30px', 'marginBottom': '20px'}),
        
        editor
    ])
    
    # Register the component's callbacks
    editor.register_callbacks(app)
    
    return app