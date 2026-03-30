"""
ChartEditorAIO - Single Chart Editor All-In-One Component
"""

import uuid
from typing import Dict, List, Any, Optional, Union

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    from dash_pydantic_form import ModelForm
    from .models import ChartConfigModel
    PYDANTIC_FORM_AVAILABLE = True
except ImportError:
    PYDANTIC_FORM_AVAILABLE = False
    ChartConfigModel = None


class ChartEditorAIO(html.Div):
    """
    A Dash All-In-One component for chart editing.
    
    Provides a chart editor interface using native Dash components with support
    for multiple chart types and data source selection.
    """
    
    class ids:
        """Component IDs for the AIO component"""
        container = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "container", "aio_id": aio_id}
        chart_type = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "chart_type", "aio_id": aio_id}
        data_source = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": aio_id}
        x_column = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "x_column", "aio_id": aio_id}
        y_column = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "y_column", "aio_id": aio_id}
        color_column = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "color_column", "aio_id": aio_id}
        size_column = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "size_column", "aio_id": aio_id}
        title = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "title", "aio_id": aio_id}
        chart = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "chart", "aio_id": aio_id}
        figure_data = lambda aio_id: {"component": "ChartEditorAIO", "subcomponent": "figure_data", "aio_id": aio_id}
    
    # Component default properties
    ids = ids
    
    @classmethod
    def get_pydantic_form_data_store_id(cls, aio_id):
        """Get the ID for the pydantic form's data store"""
        return {'part': '_pydf-main', 'aio_id': aio_id, 'form_id': f'chart-config-{aio_id}', 'parent': ''}
    
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
        aio_id: Optional[str] = None,
        flavor: str = 'pydantic_form',
        **kwargs
    ):
        """
        Initialize the ChartEditorAIO component.
        
        Args:
            data_sources: Dictionary of dataframes with names as keys
            aio_id: Unique identifier for this AIO instance
            flavor: UI flavor - 'pydantic_form'
            **kwargs: Additional properties passed to the container
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        self.aio_id = aio_id
        self.flavor = flavor
        self.data_sources = data_sources or {}
        
        # Validate flavor
        if flavor != 'pydantic_form':
            raise ValueError(f"Unsupported flavor: {flavor}. Must be: pydantic_form")
        if not PYDANTIC_FORM_AVAILABLE:
            raise ImportError("dash_pydantic_form is required for 'pydantic_form' flavor")
        
        # Build the component
        children = self._build_layout()
        
        super().__init__(
            id=self.ids.container(aio_id),
            children=children,
            **kwargs
        )
    
    def _build_layout(self):
        """Build the layout."""
        return self._build_pydantic_form_layout()
    
    def _build_pydantic_form_layout(self):
        """Build layout using dash-pydantic-form"""
        # Create a ModelForm for chart configuration
        chart_form = ModelForm(
            item=ChartConfigModel,
            form_id=f"chart-config-{self.aio_id}",
            aio_id=self.aio_id
        )
        
        return [
            html.Div([
                html.H4("Chart Editor", style={'marginBottom': '20px'}),
                
                html.Div([
                    # Left side: Configuration forms
                    html.Div([
                        html.H5("Chart Configuration"),
                        chart_form,
                        
                        html.Hr(style={'margin': '20px 0'}),
                        
                        # Data source selection (separate from pydantic form since it's dynamic)
                        html.Div([
                            html.Label("Data Source:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id=self.ids.data_source(self.aio_id),
                                options=[{'label': name, 'value': name} for name in self.data_sources.keys()],
                                value=list(self.data_sources.keys())[0] if self.data_sources else None,
                                style={'marginTop': '5px'}
                            )
                        ], style={'marginBottom': '15px'}),
                        
                        # Dynamic column controls
                        html.Div(id=f"column-controls-{self.aio_id}", children=[
                            self._build_column_controls([])
                        ])
                        
                    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '20px'}),
                    
                    # Right side: Chart display
                    html.Div([
                        dcc.Graph(
                            id=self.ids.chart(self.aio_id),
                            style={'height': '600px'}
                        ),
                        # Hidden div to store figure data
                        html.Div(id=self.ids.figure_data(self.aio_id), style={'display': 'none'})
                    ], style={'width': '68%', 'display': 'inline-block', 'marginLeft': '2%'})
                ])
            ])
        ]
    
    def _build_column_controls(self, columns):
        """Build column selection controls based on available columns"""
        if not columns:
            return html.Div("Select a data source to see column options.")
        
        column_options = [{'label': col, 'value': col} for col in columns]
        
        return html.Div([
            html.Div([
                html.Label("X Column:"),
                dcc.Dropdown(
                    id=self.ids.x_column(self.aio_id),
                    options=column_options
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Y Column:"),
                dcc.Dropdown(
                    id=self.ids.y_column(self.aio_id),
                    options=column_options
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Color Column (optional):"),
                dcc.Dropdown(
                    id=self.ids.color_column(self.aio_id),
                    options=column_options,
                    clearable=True
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Size Column (optional):"),
                dcc.Dropdown(
                    id=self.ids.size_column(self.aio_id),
                    options=column_options,
                    clearable=True
                )
            ], style={'marginBottom': '10px'})
        ])


    # @staticmethod
    # @callback(
    #     Output({"component": "ChartEditorAIO", "subcomponent": "chart", "aio_id": MATCH}, "figure"),
    #     Output({"component": "ChartEditorAIO", "subcomponent": "figure_data", "aio_id": MATCH}, "children"),
    #     [
    #         Input({"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": MATCH}, "value"),
    #         Input(self.get_pydantic_form_data_store_id(MATCH), "data"),  # form data: list of chart configs
    #     ],
    #     prevent_initial_call=True
    # )
    # def update_chart_from_form(data_source, form_data_list):
    #     # Access the data source (must be globally available)
    #     df = global_data_sources.get(data_source)
    #     if df is None or not form_data_list:
    #         fig = go.Figure()
    #         return fig, str(fig.to_dict())
    #
    #     fig = go.Figure()
    #     for form_data in form_data_list:
    #         chart_type = form_data.get("chart_type")
    #         x_col = form_data.get("x_column")
    #         y_col = form_data.get("y_column")
    #         color_col = form_data.get("color_column")
    #         size_col = form_data.get("size_column")
    #         title = form_data.get("title")
    #
    #         if chart_type == "scatter":
    #             fig.add_trace(go.Scatter(
    #                 x=df[x_col] if x_col else None,
    #                 y=df[y_col] if y_col else None,
    #                 mode="markers",
    #                 marker=dict(
    #                     color=df[color_col] if color_col else None,
    #                     size=df[size_col] if size_col else None
    #                 ),
    #                 name=title or "Scatter"
    #             ))
    #         # Add other chart types as needed...
    #
    #     fig.update_layout(title="Chart")
    #     return fig, str(fig.to_dict())
