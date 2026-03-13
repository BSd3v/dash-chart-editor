"""
MultiChartEditorAIO - Multi-Chart Editor All-In-One Component

A native Dash AIO component that provides multi-chart editing capabilities
with chart management and selection features.
"""

import json
import uuid
from typing import Dict, List, Any, Optional

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from dash_pydantic_form import ModelForm
    from .models import MultiChartConfigModel
    PYDANTIC_FORM_AVAILABLE = True
except ImportError:
    PYDANTIC_FORM_AVAILABLE = False
    MultiChartConfigModel = None

from .chart_editor_aio import ChartEditorAIO


def _first_record_dict(records: Any) -> dict:
    """Return first record when records is a non-empty list of dicts, else {}."""
    if isinstance(records, list) and len(records) > 0 and isinstance(records[0], dict):
        return records[0]
    return {}


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
        data_sources_store = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "data_sources_store", "aio_id": aio_id}
        chart_data_source = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "chart_data_source", "aio_id": aio_id}
        chart_type = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "chart_type", "aio_id": aio_id}
        x_column = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "x_column", "aio_id": aio_id}
        y_column = lambda aio_id: {"component": "MultiChartEditorAIO", "subcomponent": "y_column", "aio_id": aio_id}
    
    # Component default properties
    ids = ids
    
    @classmethod
    def get_pydantic_form_data_store_id(cls, aio_id):
        """Get the ID for the pydantic form's data store"""
        return {'part': '_pydf-main', 'aio_id': aio_id, 'form_id': f'multi-chart-config-{aio_id}', 'parent': ''}
    
    LAYOUT_MODES = [
        {'label': 'Single Chart View', 'value': 'single'},
        {'label': 'Grid View (2x2)', 'value': 'grid_2x2'},
        {'label': 'Grid View (1x3)', 'value': 'grid_1x3'},
        {'label': 'Grid View (3x1)', 'value': 'grid_3x1'}
    ]
    CHART_TYPES = [
        {'label': 'scatter', 'value': 'scatter'},
        {'label': 'line', 'value': 'line'},
        {'label': 'bar', 'value': 'bar'},
        {'label': 'histogram', 'value': 'histogram'},
        {'label': 'box', 'value': 'box'},
        {'label': 'violin', 'value': 'violin'},
        {'label': 'pie', 'value': 'pie'},
        {'label': 'heatmap', 'value': 'density_heatmap'},
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
            flavor: UI flavor - 'dcc' or 'pydantic_form'
            **kwargs: Additional properties passed to the container
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        self.aio_id = aio_id
        self.flavor = flavor
        self.data_sources = data_sources or {}
        self._serialized_data_sources = {
            name: df.to_dict("records") if hasattr(df, "to_dict") else []
            for name, df in self.data_sources.items()
        }
        if flavor not in {"dcc", "pydantic_form"}:
            raise ValueError(f"Unsupported flavor: {flavor}. Must be one of: dcc, pydantic_form")
        
        # Validate flavor
        if flavor == 'pydantic_form' and not PYDANTIC_FORM_AVAILABLE:
            raise ImportError("dash_pydantic_form is required for 'pydantic_form' flavor")
        
        # Build the component
        children = self._build_layout()
        
        super().__init__(
            id=self.ids.container(aio_id),
            children=children,
            **kwargs
        )
    
    def _build_layout(self):
        """Build the layout based on the selected flavor"""
        if self.flavor == 'pydantic_form':
            return self._build_pydantic_form_layout()
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
                
                # Hidden storage for charts data / data sources used by callbacks
                dcc.Store(id=self.ids.charts_data(self.aio_id), data="[]"),
                dcc.Store(id=self.ids.data_sources_store(self.aio_id), data=self._serialized_data_sources),
            ])
        ]
    
    def _build_pydantic_form_layout(self):
        """Build layout using dash-pydantic-form"""
        # Create a ModelForm for multi-chart configuration
        multi_chart_form = ModelForm(
            item=MultiChartConfigModel,
            form_id=f"multi-chart-config-{self.aio_id}",
            aio_id=self.aio_id
        )
        
        return [
            html.Div([
                html.H3("Multi-Chart Editor", style={'marginBottom': '20px'}),
                
                # Main layout
                html.Div([
                    # Left side: Chart management and configuration
                    html.Div([
                        html.H5("Chart Management"),
                        html.Div([
                            html.Button("Add Chart", id=self.ids.add_chart_btn(self.aio_id), 
                                      style={'marginRight': '10px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 'padding': '8px 16px'}),
                            html.Button("Remove Chart", id=self.ids.remove_chart_btn(self.aio_id),
                                      style={'backgroundColor': '#DC3545', 'color': 'white', 'border': 'none', 'padding': '8px 16px'})
                        ], style={'marginBottom': '15px'}),
                        
                        html.Div([
                            html.Label("Select Chart to Edit:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id=self.ids.selected_chart(self.aio_id),
                                placeholder="No charts created yet",
                                options=[]
                            )
                        ], style={'marginBottom': '15px'}),
                        
                        html.Hr(style={'margin': '15px 0'}),
                        
                        # Pydantic form for multi-chart configuration
                        html.Div([
                            html.H6("Display Configuration"),
                            multi_chart_form
                        ])
                    ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '20px'}),
                    
                    # Right side: Chart editor container
                    html.Div(id=self.ids.chart_editor_container(self.aio_id), children=[
                        html.Div("Select or create a chart to start editing.", 
                               style={'textAlign': 'center', 'color': '#666', 'padding': '20px'})
                    ], style={'width': '63%', 'display': 'inline-block', 'marginLeft': '2%'})
                ]),
                
                html.Hr(style={'margin': '20px 0'}),
                
                # Chart display area
                html.Div(id=self.ids.charts_display(self.aio_id), children=[
                    html.Div("No charts to display.", 
                           style={'textAlign': 'center', 'color': '#666', 'padding': '40px'})
                ], style={'width': '100%'}),
            
                # Hidden storage for charts data / data sources used by callbacks
                dcc.Store(id=self.ids.charts_data(self.aio_id), data="[]"),
                dcc.Store(id=self.ids.data_sources_store(self.aio_id), data=self._serialized_data_sources),
            ])
        ]

    # Static methods for callback registration
    @staticmethod
    @callback(
        [
            Output({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "options"),
            Output({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
            Output({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data")
        ],
        [
            Input({"component": "MultiChartEditorAIO", "subcomponent": "add_chart_btn", "aio_id": MATCH}, "n_clicks"),
            Input({"component": "MultiChartEditorAIO", "subcomponent": "remove_chart_btn", "aio_id": MATCH}, "n_clicks")
        ],
        [
            State({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
            State({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data"),
            State({"component": "MultiChartEditorAIO", "subcomponent": "data_sources_store", "aio_id": MATCH}, "data"),
        ],
        prevent_initial_call=True
    )
    def manage_charts(add_clicks, remove_clicks, selected_chart, charts_data_str, serialized_sources):
        """Handle adding and removing charts"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        trigger_component = eval(trigger_id)['subcomponent']
        
        # Parse current charts data
        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except Exception:
            charts_data = []
        data_source_names = list((serialized_sources or {}).keys())
        
        if trigger_component == 'add_chart_btn':
            # Add new chart
            new_chart_id = f"Chart {len(charts_data) + 1}"
            default_ds = data_source_names[0] if data_source_names else None
            default_records = (serialized_sources or {}).get(default_ds, []) if default_ds else []
            default_cols = list(_first_record_dict(default_records).keys())
            new_chart = {
                'id': new_chart_id,
                'title': new_chart_id,
                'type': 'scatter',
                'data_source': default_ds,
                'x_column': default_cols[0] if default_cols else None,
                'y_column': default_cols[1] if len(default_cols) > 1 else None,
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
        State({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "data_sources_store", "aio_id": MATCH}, "data"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "id"),
        prevent_initial_call=True
    )
    def update_chart_editor(selected_chart, charts_data_str, serialized_sources, selected_id):
        """Update the chart editor based on selected chart"""
        if not selected_chart:
            return html.Div("No chart selected.", 
                           style={'textAlign': 'center', 'color': 'gray', 'padding': '20px'})

        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except Exception:
            charts_data = []
        selected = next((c for c in charts_data if c.get("id") == selected_chart), None)
        if not selected:
            return html.Div("Selected chart was not found.", style={'color': 'gray'})

        aio_id = selected_id["aio_id"]
        ds_names = list((serialized_sources or {}).keys())
        ds_value = selected.get("data_source") or (ds_names[0] if ds_names else None)
        records = (serialized_sources or {}).get(ds_value, [])
        cols = list(_first_record_dict(records).keys())
        col_options = [{"label": c, "value": c} for c in cols]

        return html.Div([
            html.H5(f"Editing: {selected_chart}"),
            html.Label("Data Source"),
            dcc.Dropdown(
                id={"component": "MultiChartEditorAIO", "subcomponent": "chart_data_source", "aio_id": aio_id},
                options=[{"label": n, "value": n} for n in ds_names],
                value=ds_value,
                clearable=False,
            ),
            html.Label("Chart Type", style={"marginTop": "8px"}),
            dcc.Dropdown(
                id={"component": "MultiChartEditorAIO", "subcomponent": "chart_type", "aio_id": aio_id},
                options=MultiChartEditorAIO.CHART_TYPES,
                value=selected.get("type", "scatter"),
                clearable=False,
            ),
            html.Label("X Column", style={"marginTop": "8px"}),
            dcc.Dropdown(
                id={"component": "MultiChartEditorAIO", "subcomponent": "x_column", "aio_id": aio_id},
                options=col_options,
                value=selected.get("x_column"),
            ),
            html.Label("Y Column", style={"marginTop": "8px"}),
            dcc.Dropdown(
                id={"component": "MultiChartEditorAIO", "subcomponent": "y_column", "aio_id": aio_id},
                options=col_options,
                value=selected.get("y_column"),
            ),
            html.Div("Switch display mode to a grid view to compare multiple charts with aligned subplot axes.",
                     style={"fontSize": "12px", "color": "#666", "marginTop": "8px"}),
        ])

    @staticmethod
    @callback(
        Output({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data", allow_duplicate=True),
        Input({"component": "MultiChartEditorAIO", "subcomponent": "chart_data_source", "aio_id": MATCH}, "value"),
        Input({"component": "MultiChartEditorAIO", "subcomponent": "chart_type", "aio_id": MATCH}, "value"),
        Input({"component": "MultiChartEditorAIO", "subcomponent": "x_column", "aio_id": MATCH}, "value"),
        Input({"component": "MultiChartEditorAIO", "subcomponent": "y_column", "aio_id": MATCH}, "value"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data"),
        prevent_initial_call=True
    )
    def save_chart_config(data_source, chart_type, x_column, y_column, selected_chart, charts_data_str):
        """Persist editor changes for the currently selected chart."""
        if not selected_chart:
            return dash.no_update
        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except Exception:
            charts_data = []
        changed = False
        for chart in charts_data:
            if chart.get("id") == selected_chart:
                chart["data_source"] = data_source
                chart["type"] = chart_type or "scatter"
                chart["x_column"] = x_column
                chart["y_column"] = y_column
                changed = True
                break
        return json.dumps(charts_data) if changed else dash.no_update
    
    @staticmethod
    @callback(
        Output({"component": "MultiChartEditorAIO", "subcomponent": "charts_display", "aio_id": MATCH}, "children"),
        [
            Input({"component": "MultiChartEditorAIO", "subcomponent": "layout_mode", "aio_id": MATCH}, "value"),
            Input({"component": "MultiChartEditorAIO", "subcomponent": "charts_data", "aio_id": MATCH}, "data")
        ],
        State({"component": "MultiChartEditorAIO", "subcomponent": "selected_chart", "aio_id": MATCH}, "value"),
        State({"component": "MultiChartEditorAIO", "subcomponent": "data_sources_store", "aio_id": MATCH}, "data"),
        prevent_initial_call=True
    )
    def update_charts_display(layout_mode, charts_data_str, selected_chart, serialized_sources):
        """Update the charts display based on layout mode and available charts"""
        try:
            charts_data = json.loads(charts_data_str) if charts_data_str else []
        except Exception:
            charts_data = []
        
        if not charts_data:
            return html.Div("No charts to display.", 
                           style={'textAlign': 'center', 'color': 'gray', 'padding': '50px'})
        
        if layout_mode == 'single':
            chart = next((c for c in charts_data if c.get("id") == selected_chart), None) or (
                charts_data[0] if charts_data else None
            )
            if chart is None:
                return html.Div("No chart selected.", style={'color': 'gray'})
            ds_name = chart.get("data_source")
            records = (serialized_sources or {}).get(ds_name, [])
            if not records:
                return html.Div(f"No data source found for {chart.get('id')}", style={'color': 'gray'})
            df = pd.DataFrame(records)
            chart_type = chart.get("type", "scatter")
            if not hasattr(px, chart_type):
                return html.Div(f"Unsupported chart type: {chart_type}", style={'color': 'gray'})
            fn = getattr(px, chart_type)
            kwargs = {}
            if chart.get("x_column"):
                kwargs["x"] = chart["x_column"]
            if chart.get("y_column"):
                kwargs["y"] = chart["y_column"]
            fig = fn(data_frame=df, **kwargs)
            fig.update_layout(title=chart.get('title', chart.get('id', 'Chart')))
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
                subplot_titles=[chart.get('title', f'Chart {i+1}') for i, chart in enumerate(charts_data[:rows*cols])],
                shared_xaxes=True,
                shared_yaxes=True,
            )
            
            # Add each configured chart to its own subplot with aligned axes
            for i, chart in enumerate(charts_data[:rows*cols]):
                row = (i // cols) + 1
                col = (i % cols) + 1
                ds_name = chart.get("data_source")
                records = (serialized_sources or {}).get(ds_name, [])
                if not records:
                    continue
                df = pd.DataFrame(records)
                chart_type = chart.get("type", "scatter")
                if not hasattr(px, chart_type):
                    continue
                fn = getattr(px, chart_type)
                kwargs = {}
                if chart.get("x_column"):
                    kwargs["x"] = chart["x_column"]
                if chart.get("y_column"):
                    kwargs["y"] = chart["y_column"]
                try:
                    sub_fig = fn(data_frame=df, **kwargs)
                    for trace in sub_fig.data:
                        fig.add_trace(trace, row=row, col=col)
                except Exception:
                    fig.add_trace(
                        go.Scatter(x=[], y=[], mode="markers", name=f"{chart.get('id')} (error)"),
                        row=row, col=col,
                    )
            
            fig.update_layout(height=600, showlegend=False)
            return dcc.Graph(figure=fig)
        
        return html.Div("Invalid layout mode.")
