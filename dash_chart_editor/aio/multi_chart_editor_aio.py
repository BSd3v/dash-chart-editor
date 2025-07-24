"""
MultiChartEditorAIO - Multi-Chart Editor All-In-One Component

A native Dash AIO component that provides multi-chart editing capabilities
with chart management and selection features.
"""

import uuid
from typing import Dict, List, Any, Optional

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import dash_mantine_components as dmc
    DMC_AVAILABLE = True
except ImportError:
    DMC_AVAILABLE = False

from .chart_editor_aio import ChartEditorAIO


class MultiChartEditorAIO(html.Div):
    """
    A Dash All-In-One component for managing multiple charts.
    
    Provides an interface for creating, editing, and managing multiple charts
    with the ability to switch between them and view them in a grid layout.
    """
    
    class ids:
        """Component IDs for the AIO component"""
        container = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "container", "aio_id": aio_id}
        chart_list = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "chart_list", "aio_id": aio_id}
        selected_chart = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": aio_id}
        add_chart_btn = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "add_chart_btn", "aio_id": aio_id}
        remove_chart_btn = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "remove_chart_btn", "aio_id": aio_id}
        chart_editor_container = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "chart_editor_container", "aio_id": aio_id}
        charts_display = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "charts_display", "aio_id": aio_id}
        layout_mode = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "layout_mode", "aio_id": aio_id}
        charts_data = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": aio_id}
    
    # Component default properties
    ids = ids
    
    LAYOUT_MODES = [
        {'label': 'Single Chart View', 'value': 'single'},
        {'label': 'Grid View (2x2)', 'value': 'grid_2x2'},
        {'label': 'Grid View (1x3)', 'value': 'grid_1x3'},
        {'label': 'Grid View (3x1)', 'value': 'grid_3x1'}
    ]
    
    def __init__(
        self,
        data_sources: Optional[Dict[str, Any]] = None,
        aio_id: Optional[str] = None,
        flavor: str = 'dcc',
        **kwargs
    ):
        """
        Initialize the MultiChartEditorAIO component.
        
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
        return [
            html.Div([
                html.H3("Multi-Chart Editor", style={'marginBottom': '20px'}),
                
                # Chart management section
                html.Div([
                    html.Div([
                        html.H5("Chart Management"),
                        html.Div([
                            html.Button("Add Chart", id=self.ids.add_chart_btn(self.aio_id), 
                                      className="btn btn-primary", 
                                      style={'marginRight': '10px'}),
                            html.Button("Remove Chart", id=self.ids.remove_chart_btn(self.aio_id),
                                      className="btn btn-danger")
                        ], style={'marginBottom': '15px'}),
                        
                        html.Label("Select Chart to Edit:"),
                        dcc.Dropdown(
                            id=self.ids.selected_chart(self.aio_id),
                            options=[],
                            value=None,
                            placeholder="No charts created yet"
                        ),
                        
                        html.Div(style={'height': '20px'}),
                        
                        html.Label("Display Mode:"),
                        dcc.Dropdown(
                            id=self.ids.layout_mode(self.aio_id),
                            options=self.LAYOUT_MODES,
                            value='single',
                            clearable=False
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    # Chart editor container
                    html.Div(id=self.ids.chart_editor_container(self.aio_id), children=[
                        html.Div("Select or create a chart to start editing.", 
                               style={'textAlign': 'center', 'color': 'gray', 'padding': '20px'})
                    ])
                ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}),
                
                # Charts display area
                html.Div([
                    html.Div(id=self.ids.charts_display(self.aio_id), children=[
                        html.Div("No charts to display.", 
                               style={'textAlign': 'center', 'color': 'gray', 'padding': '50px'})
                    ])
                ], style={'width': '63%', 'display': 'inline-block', 'marginLeft': '2%'}),
                
                # Hidden storage for charts data
                html.Div(id=self.ids.charts_data(self.aio_id), style={'display': 'none'}, children="[]")
            ])
        ]
    
    def _build_dmc_layout(self):
        """Build layout using DMC components"""
        return [
            dmc.Container([
                dmc.Title("Multi-Chart Editor", order=3, mb="md"),
                
                dmc.Grid([
                    dmc.Col([
                        dmc.Stack([
                            dmc.Title("Chart Management", order=5),
                            
                            dmc.Group([
                                dmc.Button("Add Chart", id=self.ids.add_chart_btn(self.aio_id), color="blue"),
                                dmc.Button("Remove Chart", id=self.ids.remove_chart_btn(self.aio_id), color="red")
                            ]),
                            
                            dmc.Select(
                                label="Select Chart to Edit",
                                placeholder="No charts created yet",
                                data=[],
                                id=self.ids.selected_chart(self.aio_id)
                            ),
                            
                            dmc.Select(
                                label="Display Mode",
                                data=self.LAYOUT_MODES,
                                value='single',
                                id=self.ids.layout_mode(self.aio_id)
                            )
                        ]),
                        
                        # Chart editor container
                        html.Div(id=self.ids.chart_editor_container(self.aio_id), children=[
                            dmc.Text("Select or create a chart to start editing.", 
                                   align="center", color="dimmed", p="md")
                        ])
                    ], span=5),
                    
                    dmc.Col([
                        html.Div(id=self.ids.charts_display(self.aio_id), children=[
                            dmc.Text("No charts to display.", align="center", color="dimmed", p="xl")
                        ])
                    ], span=7)
                ]),
                
                # Hidden storage for charts data
                html.Div(id=self.ids.charts_data(self.aio_id), style={'display': 'none'}, children="[]")
            ])
        ]

    # Static methods for callback registration
    @staticmethod
    @callback(
        [
            Output({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "options"),
            Output({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
            Output({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "children")
        ],
        [
            Input({"component": "MultiChartEditorAIO", "subcomponent": "add_chart_btn", "aio_id": MATCH}, "n_clicks"),
            Input({"component": "MultiChartEditorAIO", "subcomponent": "remove_chart_btn", "aio_id": MATCH}, "n_clicks")
        ],
        [
            State({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
            State({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "children")
        ],
        prevent_initial_call=True
    )
    def manage_charts(add_clicks, remove_clicks, selected_chart, charts_data_str):
        """Handle adding and removing charts"""
        import json
        
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        trigger_component = eval(trigger_id)['subcomponent']
        
        # Parse current charts data
        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except:
            charts_data = []
        
        if trigger_component == 'add_chart_btn':
            # Add new chart
            new_chart_id = f"Chart {len(charts_data) + 1}"
            new_chart = {
                'id': new_chart_id,
                'title': new_chart_id,
                'type': 'scatter',
                'data_source': None,
                'x_column': None,
                'y_column': None,
                'color_column': None,
                'size_column': None
            }
            charts_data.append(new_chart)
            selected_value = new_chart_id
            
        elif trigger_component == 'remove_chart_btn' and selected_chart:
            # Remove selected chart
            charts_data = [chart for chart in charts_data if chart['id'] != selected_chart]
            selected_value = charts_data[0]['id'] if charts_data else None
            
        else:
            return dash.no_update, dash.no_update, dash.no_update
        
        # Update options
        options = [{'label': chart['id'], 'value': chart['id']} for chart in charts_data]
        
        return options, selected_value, json.dumps(charts_data)
    
    @staticmethod
    @callback(
        Output({"component": "MultiChartEditorAIO", "subcomponent": "chart_editor_container", "aio_id": MATCH}, "children"),
        Input({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "children"),
        prevent_initial_call=True
    )
    def update_chart_editor(selected_chart, charts_data_str):
        """Update the chart editor based on selected chart"""
        if not selected_chart:
            return html.Div("No chart selected.", 
                           style={'textAlign': 'center', 'color': 'gray', 'padding': '20px'})
        
        # In a real implementation, this would create a ChartEditorAIO instance
        # configured with the selected chart's data
        return html.Div([
            html.H5(f"Editing: {selected_chart}"),
            html.Div("Chart editor controls would go here.", 
                    style={'color': 'gray', 'fontStyle': 'italic'})
        ])
    
    @staticmethod
    @callback(
        Output({"component": "MultiChartEditorAIO", "subcomponent": "charts_display", "aio_id": MATCH}, "children"),
        [
            Input({"component": "MultiChartEditorAIO", "subcomponent": "layout_mode", "aio_id": MATCH}, "value"),
            Input({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "children")
        ],
        prevent_initial_call=True
    )
    def update_charts_display(layout_mode, charts_data_str):
        """Update the charts display based on layout mode and available charts"""
        import json
        
        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except:
            charts_data = []
        
        if not charts_data:
            return html.Div("No charts to display.", 
                           style={'textAlign': 'center', 'color': 'gray', 'padding': '50px'})
        
        if layout_mode == 'single':
            # Show single chart (first one for now)
            chart = charts_data[0]
            fig = go.Figure()
            fig.update_layout(title=chart.get('title', 'Chart'))
            return dcc.Graph(figure=fig, style={'height': '500px'})
        
        elif layout_mode in ['grid_2x2', 'grid_1x3', 'grid_3x1']:
            # Create subplot layout
            if layout_mode == 'grid_2x2':
                rows, cols = 2, 2
            elif layout_mode == 'grid_1x3':
                rows, cols = 1, 3
            else:  # grid_3x1
                rows, cols = 3, 1
            
            # Create subplots
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[chart.get('title', f'Chart {i+1}') for i, chart in enumerate(charts_data[:rows*cols])]
            )
            
            # Add placeholder data to each subplot
            for i, chart in enumerate(charts_data[:rows*cols]):
                row = (i // cols) + 1
                col = (i % cols) + 1
                fig.add_scatter(x=[1, 2, 3], y=[1, 4, 2], name=chart.get('title', f'Chart {i+1}'),
                              row=row, col=col)
            
            fig.update_layout(height=600, showlegend=False)
            return dcc.Graph(figure=fig)
        
        return html.Div("Invalid layout mode.")