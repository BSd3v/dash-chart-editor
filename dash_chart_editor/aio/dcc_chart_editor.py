"""
DCCChartEditor - Chart Editor using standard DCC components

A standalone chart editor component that uses only DCC components
for a clean, simple interface without external dependencies.
"""

import uuid
from typing import Dict, List, Any, Optional, Union

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class DCCChartEditor(html.Div):
    """
    A standalone chart editor using DCC components only.
    
    This component is separate from the AIO pattern to avoid callback conflicts
    and provides a clean DCC-only interface.
    """
    
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
    
    def __init__(
        self,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None,
        component_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the DCCChartEditor component.
        
        Args:
            data_sources: Dictionary of dataframes with names as keys
            component_id: Unique identifier for this component instance
            **kwargs: Additional properties passed to the container
        """
        if component_id is None:
            component_id = str(uuid.uuid4())
        
        self.component_id = component_id
        self.data_sources = data_sources or {}
        
        # Build the component
        children = self._build_layout()
        
        super().__init__(
            id=f"dcc-chart-editor-{component_id}",
            children=children,
            **kwargs
        )
    
    def _build_layout(self):
        """Build the layout using DCC components"""
        data_source_options = [{'label': name, 'value': name} for name in self.data_sources.keys()]
        
        return [
            html.Div([
                html.H4("DCC Chart Editor", style={'marginBottom': '20px'}),
                
                # Chart configuration controls
                html.Div([
                    html.Div([
                        html.Label("Chart Type:"),
                        dcc.Dropdown(
                            id=f"chart-type-{self.component_id}",
                            options=self.CHART_TYPES,
                            value='scatter',
                            clearable=False
                        )
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.Label("Data Source:"),
                        dcc.Dropdown(
                            id=f"data-source-{self.component_id}",
                            options=data_source_options,
                            value=list(self.data_sources.keys())[0] if self.data_sources else None,
                            clearable=False
                        )
                    ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
                ], style={'marginBottom': '20px'}),
                
                # Column selection controls
                html.Div(id=f"column-controls-{self.component_id}", children=[
                    self._build_column_controls([])
                ]),
                
                # Chart title
                html.Div([
                    html.Label("Chart Title:"),
                    dcc.Input(
                        id=f"title-{self.component_id}",
                        type='text',
                        placeholder='Enter chart title...',
                        style={'width': '100%'}
                    )
                ], style={'marginBottom': '20px'}),
                
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
    
    def _build_column_controls(self, columns):
        """Build column selection controls based on available columns"""
        if not columns:
            return html.Div("Select a data source to see column options.", style={'color': '#666'})
        
        column_options = [{'label': col, 'value': col} for col in columns]
        
        return html.Div([
            html.Div([
                html.Label("X Column:"),
                dcc.Dropdown(
                    id=f"x-column-{self.component_id}",
                    options=column_options
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Y Column:"),
                dcc.Dropdown(
                    id=f"y-column-{self.component_id}",
                    options=column_options
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Color Column (optional):"),
                dcc.Dropdown(
                    id=f"color-column-{self.component_id}",
                    options=column_options,
                    clearable=True
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Size Column (optional):"),
                dcc.Dropdown(
                    id=f"size-column-{self.component_id}",
                    options=column_options,
                    clearable=True
                )
            ], style={'marginBottom': '10px'})
        ])
    
    def register_callbacks(self, app):
        """Register callbacks for this component instance"""
        
        # Update column controls when data source changes
        @app.callback(
            Output(f"column-controls-{self.component_id}", "children"),
            Input(f"data-source-{self.component_id}", "value")
        )
        def update_column_options(data_source):
            """Update column selection options when data source changes"""
            if not data_source or data_source not in self.data_sources:
                return self._build_column_controls([])
            
            df = self.data_sources[data_source]
            columns = df.columns.tolist()
            return self._build_column_controls(columns)
        
        # Update chart based on selections
        @app.callback(
            [
                Output(f"chart-{self.component_id}", "figure"),
                Output(f"debug-info-{self.component_id}", "children")
            ],
            [
                Input(f"chart-type-{self.component_id}", "value"),
                Input(f"data-source-{self.component_id}", "value"),
                Input(f"x-column-{self.component_id}", "value"),
                Input(f"y-column-{self.component_id}", "value"),
                Input(f"color-column-{self.component_id}", "value"),
                Input(f"size-column-{self.component_id}", "value"),
                Input(f"title-{self.component_id}", "value"),
            ],
            prevent_initial_call=True
        )
        def update_chart(chart_type, data_source, x_col, y_col, color_col, size_col, title):
            """Update chart based on user selections"""
            
            if not data_source or data_source not in self.data_sources:
                fig = go.Figure()
                fig.update_layout(title="Select a data source")
                return fig, "Waiting for data source selection..."
            
            if not x_col and chart_type not in ['histogram']:
                fig = go.Figure()
                fig.update_layout(title="Select X column")
                return fig, "Waiting for column selection..."
            
            # Get the data
            df = self.data_sources[data_source]
            
            # Create chart based on type
            try:
                if chart_type == 'scatter':
                    if not y_col:
                        fig = go.Figure()
                        fig.update_layout(title="Scatter plot requires Y column")
                        return fig, "Missing Y column for scatter plot"
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
                
                elif chart_type == 'line':
                    if not y_col:
                        fig = go.Figure()
                        fig.update_layout(title="Line chart requires Y column")
                        return fig, "Missing Y column for line chart"
                    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
                
                elif chart_type == 'bar':
                    if not y_col:
                        fig = go.Figure()
                        fig.update_layout(title="Bar chart requires Y column")
                        return fig, "Missing Y column for bar chart"
                    fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
                
                elif chart_type == 'histogram':
                    fig = px.histogram(df, x=x_col, color=color_col, title=title)
                
                elif chart_type == 'box':
                    if not y_col:
                        fig = px.box(df, y=x_col, color=color_col, title=title)
                    else:
                        fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
                
                elif chart_type == 'violin':
                    if not y_col:
                        fig = px.violin(df, y=x_col, color=color_col, title=title)
                    else:
                        fig = px.violin(df, x=x_col, y=y_col, color=color_col, title=title)
                
                elif chart_type == 'pie':
                    if not y_col:
                        fig = go.Figure()
                        fig.update_layout(title="Pie chart requires both name (X) and value (Y) columns")
                        return fig, "Pie chart needs both X and Y columns"
                    fig = px.pie(df, names=x_col, values=y_col, title=title)
                
                elif chart_type == 'heatmap':
                    # For heatmap, use correlation matrix of numeric columns
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) >= 2:
                        corr_df = df[numeric_cols].corr()
                        fig = px.imshow(corr_df, title=title or "Correlation Heatmap", aspect="auto")
                    else:
                        fig = go.Figure()
                        fig.update_layout(title="Heatmap requires numeric columns")
                        return fig, "Not enough numeric columns for heatmap"
                
                else:
                    fig = go.Figure()
                    fig.update_layout(title="Unsupported chart type")
                    return fig, f"Unsupported chart type: {chart_type}"
                
                fig.update_layout(height=550)
                debug_info = f"Chart: {chart_type}, Data: {data_source}, X: {x_col}, Y: {y_col}"
                return fig, debug_info
                
            except Exception as e:
                fig = go.Figure()
                fig.update_layout(title=f"Error creating chart: {str(e)}")
                return fig, f"Error: {str(e)}"


def create_dcc_chart_editor_app(data_sources: Dict[str, pd.DataFrame], port: int = 8055):
    """
    Create a standalone Dash app with DCCChartEditor.
    
    Args:
        data_sources: Dictionary of dataframes
        port: Port to run the app on
    
    Returns:
        Dash app instance
    """
    app = dash.Dash(__name__)
    
    # Create the editor component
    editor = DCCChartEditor(
        data_sources=data_sources,
        component_id="main-editor"
    )
    
    app.layout = html.Div([
        html.Div([
            html.H1("DCC Chart Editor", 
                   style={'textAlign': 'center', 'marginBottom': '10px'}),
            html.P("Chart editor using standard DCC components only.", 
                  style={'textAlign': 'center', 'color': '#666', 'fontSize': '18px', 'marginBottom': '30px'})
        ], style={'backgroundColor': '#f8f9fa', 'padding': '30px', 'marginBottom': '20px'}),
        
        editor
    ])
    
    # Register the component's callbacks
    editor.register_callbacks(app)
    
    return app