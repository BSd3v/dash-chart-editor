"""
ChartEditorAIO - Single Chart Editor All-In-One Component

A native Dash AIO component that provides chart editing capabilities
using standard Dash components instead of react-chart-editor.
"""

import uuid
from typing import Dict, List, Any, Optional, Union

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    import dash_mantine_components as dmc
    DMC_AVAILABLE = True
except ImportError:
    DMC_AVAILABLE = False


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
        flavor: str = 'dcc',
        **kwargs
    ):
        """
        Initialize the ChartEditorAIO component.
        
        Args:
            data_sources: Dictionary of dataframes with names as keys
            aio_id: Unique identifier for this AIO instance
            flavor: UI flavor - 'dcc' or 'dmc'
            **kwargs: Additional properties passed to the container
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        self.aio_id = aio_id
        self.flavor = flavor
        self.data_sources = data_sources or {}
        
        # Validate flavor
        if flavor == 'dmc' and not DMC_AVAILABLE:
            raise ImportError("dash_mantine_components is required for 'dmc' flavor")
        
        # Build the component
        children = self._build_layout()
        
        super().__init__(
            id=self.ids.container(aio_id),
            children=children,
            **kwargs
        )
    
    def _build_layout(self):
        """Build the layout based on the selected flavor"""
        if self.flavor == 'dmc':
            return self._build_dmc_layout()
        else:
            return self._build_dcc_layout()
    
    def _build_dcc_layout(self):
        """Build layout using DCC components"""
        data_source_options = [{'label': name, 'value': name} for name in self.data_sources.keys()]
        
        return [
            html.Div([
                html.H4("Chart Editor", style={'marginBottom': '20px'}),
                
                # Chart configuration controls
                html.Div([
                    html.Div([
                        html.Label("Chart Type:"),
                        dcc.Dropdown(
                            id=self.ids.chart_type(self.aio_id),
                            options=self.CHART_TYPES,
                            value='scatter',
                            clearable=False
                        )
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.Label("Data Source:"),
                        dcc.Dropdown(
                            id=self.ids.data_source(self.aio_id),
                            options=data_source_options,
                            value=list(self.data_sources.keys())[0] if self.data_sources else None,
                            clearable=False
                        )
                    ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
                ], style={'marginBottom': '20px'}),
                
                # Column selection controls
                html.Div(id=f"column-controls-{self.aio_id}", children=[
                    self._build_column_controls([])
                ]),
                
                # Chart title
                html.Div([
                    html.Label("Chart Title:"),
                    dcc.Input(
                        id=self.ids.title(self.aio_id),
                        type='text',
                        placeholder='Enter chart title...',
                        style={'width': '100%'}
                    )
                ], style={'marginBottom': '20px'}),
                
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}),
            
            # Chart display area
            html.Div([
                dcc.Graph(
                    id=self.ids.chart(self.aio_id),
                    style={'height': '600px'}
                ),
                # Hidden div to store figure data
                html.Div(id=self.ids.figure_data(self.aio_id), style={'display': 'none'})
            ], style={'width': '68%', 'display': 'inline-block', 'marginLeft': '2%'})
        ]
    
    def _build_dmc_layout(self):
        """Build layout using DMC components"""
        data_source_options = [{'label': name, 'value': name} for name in self.data_sources.keys()]
        
        return [
            dmc.Container([
                dmc.Title("Chart Editor", order=4, mb="md"),
                
                dmc.Grid([
                    dmc.Col([
                        # Chart configuration controls
                        dmc.Stack([
                            dmc.Select(
                                label="Chart Type",
                                data=self.CHART_TYPES,
                                value='scatter',
                                id=self.ids.chart_type(self.aio_id)
                            ),
                            
                            dmc.Select(
                                label="Data Source",
                                data=data_source_options,
                                value=list(self.data_sources.keys())[0] if self.data_sources else None,
                                id=self.ids.data_source(self.aio_id)
                            ),
                            
                            # Column controls will be added dynamically
                            html.Div(id=f"column-controls-{self.aio_id}", children=[
                                self._build_column_controls([])
                            ]),
                            
                            dmc.TextInput(
                                label="Chart Title",
                                placeholder="Enter chart title...",
                                id=self.ids.title(self.aio_id)
                            )
                        ])
                    ], span=4),
                    
                    dmc.Col([
                        dcc.Graph(
                            id=self.ids.chart(self.aio_id),
                            style={'height': '600px'}
                        ),
                        # Hidden div to store figure data
                        html.Div(id=self.ids.figure_data(self.aio_id), style={'display': 'none'})
                    ], span=8)
                ])
            ])
        ]
    
    def _build_column_controls(self, columns):
        """Build column selection controls based on available columns"""
        if not columns:
            return html.Div("Select a data source to see column options.")
        
        column_options = [{'label': col, 'value': col} for col in columns]
        
        if self.flavor == 'dmc':
            return dmc.Stack([
                dmc.Select(
                    label="X Column",
                    data=column_options,
                    id=self.ids.x_column(self.aio_id)
                ),
                dmc.Select(
                    label="Y Column",
                    data=column_options,
                    id=self.ids.y_column(self.aio_id)
                ),
                dmc.Select(
                    label="Color Column (optional)",
                    data=column_options,
                    id=self.ids.color_column(self.aio_id),
                    clearable=True
                ),
                dmc.Select(
                    label="Size Column (optional)",
                    data=column_options,
                    id=self.ids.size_column(self.aio_id),
                    clearable=True
                )
            ])
        else:
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

    # Static methods for callback registration
    @staticmethod
    @callback(
        Output({"component": "ChartEditorAIO", "subcomponent": "chart", "aio_id": MATCH}, "figure"),
        Output({"component": "ChartEditorAIO", "subcomponent": "figure_data", "aio_id": MATCH}, "children"),
        [
            Input({"component": "ChartEditorAIO", "subcomponent": "chart_type", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "x_column", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "y_column", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "color_column", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "size_column", "aio_id": MATCH}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "title", "aio_id": MATCH}, "value"),
        ],
        prevent_initial_call=True
    )
    def update_chart(chart_type, data_source, x_col, y_col, color_col, size_col, title):
        """Update chart based on user selections"""
        # This would need access to the data_sources, which requires a different approach
        # For now, return an empty figure
        ctx = dash.callback_context
        if not ctx.triggered:
            return go.Figure(), ""
        
        # Get the AIO ID from the triggered component
        aio_id = ctx.triggered[0]['prop_id'].split('.')[0]
        aio_id = eval(aio_id)['aio_id']
        
        # In a real implementation, we'd need to access the data_sources
        # This is a limitation of the current AIO pattern - we need to store data globally
        
        fig = go.Figure()
        fig.update_layout(title=title or "Chart")
        
        return fig, str(fig.to_dict())


# Global callback for updating column controls when data source changes
@callback(
    Output({"component": "ChartEditorAIO", "subcomponent": "container", "aio_id": ALL}, "children"),
    Input({"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": ALL}, "value"),
    State({"component": "ChartEditorAIO", "subcomponent": "container", "aio_id": ALL}, "children"),
    prevent_initial_call=True
)
def update_column_options(data_sources, current_children):
    """Update column selection options when data source changes"""
    # This callback needs to be implemented in the application using the component
    # as it requires access to the actual data
    return dash.no_update