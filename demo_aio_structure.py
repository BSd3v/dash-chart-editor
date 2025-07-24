"""
Interactive Demo: AIO Component Structure

This script demonstrates the structure and capabilities of the new AIO components
for dash-chart-editor. It shows the component hierarchy, available features,
and provides a quick way to test the implementation.
"""

import dash
from dash import html, dcc, Input, Output, callback, clientside_callback, ClientsideFunction
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Import the AIO components
try:
    from dash_chart_editor.aio import ChartEditorAIO, MultiChartEditorAIO
    AIO_AVAILABLE = True
except ImportError:
    AIO_AVAILABLE = False

# Sample datasets for demonstration
SAMPLE_DATA = {
    'Iris Dataset': px.data.iris(),
    'Tips Dataset': px.data.tips(),
    'Gapminder Dataset': px.data.gapminder().query("year == 2007"),
    'Stocks Dataset': px.data.stocks()
}

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
])

app.title = "AIO Components Demo - Structure Explorer"

def create_component_info_card(title, description, features, usage_example):
    """Create an information card for a component"""
    return html.Div([
        html.Div([
            html.H4(title, className="card-title"),
            html.P(description, className="card-text"),
            html.H6("Key Features:", className="mt-3"),
            html.Ul([html.Li(feature) for feature in features], className="list-unstyled"),
            html.H6("Usage Example:", className="mt-3"),
            html.Pre(html.Code(usage_example), className="bg-light p-2 rounded")
        ], className="card-body")
    ], className="card h-100")

def create_architecture_diagram():
    """Create a visual representation of the AIO architecture"""
    return html.Div([
        html.H4("AIO Architecture Overview", className="text-center mb-4"),
        html.Div([
            # Main Components
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line fa-3x mb-3"),
                    html.H5("ChartEditorAIO"),
                    html.P("Single chart editing with configurable UI flavors")
                ], className="text-center p-3 border rounded"),
            ], className="col-md-6 mb-3"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-th fa-3x mb-3"),
                    html.H5("MultiChartEditorAIO"),
                    html.P("Multi-chart management with layout options")
                ], className="text-center p-3 border rounded"),
            ], className="col-md-6 mb-3"),
            
            # UI Flavors
            html.Div([
                html.H6("UI Flavors Available:"),
                html.Div([
                    html.Span("DCC Flavor", className="badge bg-primary me-2"),
                    html.Span("DMC Flavor", className="badge bg-success")
                ])
            ], className="col-12 text-center mt-3")
            
        ], className="row")
    ], className="card-body")

def create_data_structure_info():
    """Create information about data structure requirements"""
    return html.Div([
        html.H5("Data Structure Requirements"),
        html.P("The AIO components work with pandas DataFrames provided as a dictionary:"),
        html.Pre(html.Code("""
data_sources = {
    'Dataset Name': pandas_dataframe,
    'Another Dataset': another_dataframe
}

# Example with sample data
import plotly.express as px

data_sources = {
    'Iris': px.data.iris(),
    'Tips': px.data.tips()
}
        """), className="bg-light p-3 rounded"),
        
        html.H6("Supported Chart Types:", className="mt-3"),
        html.Div([
            html.Span(chart_type['label'], className="badge bg-info me-1 mb-1") 
            for chart_type in ChartEditorAIO.CHART_TYPES if AIO_AVAILABLE
        ] if AIO_AVAILABLE else [html.Span("AIO components not available", className="text-muted")])
    ])

# Define the app layout
if AIO_AVAILABLE:
    layout = html.Div([
        # Header
        html.Div([
            html.H1("AIO Components Structure Demo", className="text-center text-white"),
            html.P("Explore the new Dash All-In-One components for chart editing", 
                   className="text-center text-white-50")
        ], className="bg-dark py-4 mb-4"),
        
        # Navigation tabs
        html.Div([
            dcc.Tabs(id="demo-tabs", value="overview", children=[
                dcc.Tab(label="Overview", value="overview"),
                dcc.Tab(label="Single Chart Demo", value="single-demo"),
                dcc.Tab(label="Multi-Chart Demo", value="multi-demo"),
                dcc.Tab(label="Component Structure", value="structure"),
                dcc.Tab(label="Migration Guide", value="migration")
            ])
        ], className="container-fluid mb-4"),
        
        # Content area
        html.Div(id="tab-content", className="container-fluid"),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P("Dash Chart Editor - AIO Components Demo", className="text-center text-muted")
        ], className="mt-5")
    ])
else:
    layout = html.Div([
        html.Div([
            html.H1("AIO Components Not Available", className="text-center"),
            html.P("The AIO components could not be imported. Please ensure the implementation is complete.", 
                   className="text-center text-muted"),
            html.Hr(),
            html.P("Expected structure:", className="mt-3"),
            html.Pre("""
dash_chart_editor/
├── aio/
│   ├── __init__.py
│   ├── chart_editor_aio.py
│   └── multi_chart_editor_aio.py
└── ...
            """, className="bg-light p-3")
        ], className="container py-5")
    ])

app.layout = layout

# Callbacks for tab content
if AIO_AVAILABLE:
    @callback(
        Output("tab-content", "children"),
        Input("demo-tabs", "value")
    )
    def render_tab_content(active_tab):
        if active_tab == "overview":
            return html.Div([
                create_architecture_diagram(),
                html.Div([
                    html.Div([
                        create_component_info_card(
                            "ChartEditorAIO",
                            "A single chart editor component providing native Dash-based chart editing capabilities.",
                            [
                                "8 chart types supported",
                                "Dynamic data source selection",
                                "Real-time chart updates",
                                "DCC and DMC flavor support"
                            ],
                            """ChartEditorAIO(
    data_sources=data_dict,
    aio_id="my-editor",
    flavor="dcc"
)"""
                        )
                    ], className="col-md-6 mb-4"),
                    
                    html.Div([
                        create_component_info_card(
                            "MultiChartEditorAIO",
                            "A multi-chart management component for creating and managing multiple charts.",
                            [
                                "Multiple chart creation",
                                "Chart selection and editing",
                                "Multiple layout modes",
                                "Grid and single view options"
                            ],
                            """MultiChartEditorAIO(
    data_sources=data_dict,
    aio_id="multi-editor",
    flavor="dcc"
)"""
                        )
                    ], className="col-md-6 mb-4")
                ], className="row"),
                
                html.Div([
                    create_data_structure_info()
                ], className="mt-4")
            ])
        
        elif active_tab == "single-demo":
            return html.Div([
                html.H3("Single Chart Editor Demo"),
                html.P("This demonstrates the ChartEditorAIO component in action:"),
                ChartEditorAIO(
                    data_sources=SAMPLE_DATA,
                    aio_id="demo-single",
                    flavor="dcc"
                ),
                dcc.Store(id="demo-data-store", data={
                    name: df.to_dict('records') for name, df in SAMPLE_DATA.items()
                })
            ])
        
        elif active_tab == "multi-demo":
            return html.Div([
                html.H3("Multi-Chart Editor Demo"),
                html.P("This demonstrates the MultiChartEditorAIO component:"),
                MultiChartEditorAIO(
                    data_sources=SAMPLE_DATA,
                    aio_id="demo-multi",
                    flavor="dcc"
                )
            ])
        
        elif active_tab == "structure":
            return html.Div([
                html.H3("Component Structure Analysis"),
                html.Div([
                    html.H5("ChartEditorAIO Component IDs:"),
                    html.Pre(json.dumps({
                        "container": ChartEditorAIO.ids.container("example"),
                        "chart_type": ChartEditorAIO.ids.chart_type("example"),
                        "data_source": ChartEditorAIO.ids.data_source("example"),
                        "x_column": ChartEditorAIO.ids.x_column("example"),
                        "y_column": ChartEditorAIO.ids.y_column("example"),
                        "chart": ChartEditorAIO.ids.chart("example")
                    }, indent=2), className="bg-light p-3"),
                    
                    html.H5("MultiChartEditorAIO Component IDs:", className="mt-4"),
                    html.Pre(json.dumps({
                        "container": MultiChartEditorAIO.ids.container("example"),
                        "selected_chart": MultiChartEditorAIO.ids.selected_chart("example"),
                        "add_chart_btn": MultiChartEditorAIO.ids.add_chart_btn("example"),
                        "charts_display": MultiChartEditorAIO.ids.charts_display("example"),
                        "layout_mode": MultiChartEditorAIO.ids.layout_mode("example")
                    }, indent=2), className="bg-light p-3")
                ])
            ])
        
        elif active_tab == "migration":
            return html.Div([
                html.H3("Migration from react-chart-editor"),
                html.Div([
                    html.H5("Before (react-chart-editor):"),
                    html.Pre("""
from dash_chart_editor import DashChartEditor

layout = html.Div([
    DashChartEditor(
        dataSources=data_sources,
        figure=figure
    )
])
                    """, className="bg-light p-3"),
                    
                    html.H5("After (AIO Components):"),
                    html.Pre("""
from dash_chart_editor.aio import ChartEditorAIO

layout = html.Div([
    ChartEditorAIO(
        data_sources=data_sources,
        aio_id="editor-1",
        flavor="dcc"
    )
])

# Additional callbacks needed for data handling
@callback(...)
def update_chart_with_data(...):
    # Handle chart updates with actual data
    pass
                    """, className="bg-light p-3"),
                    
                    html.Div([
                        html.H6("Key Benefits of Migration:"),
                        html.Ul([
                            html.Li("Native Dash components - no external React dependencies"),
                            html.Li("Full control over styling and behavior"),
                            html.Li("Better integration with Dash ecosystem"),
                            html.Li("Support for multiple UI flavors (DCC/DMC)"),
                            html.Li("Modular design for specific use cases")
                        ])
                    ], className="alert alert-info")
                ])
            ])
        
        return html.Div("Select a tab to view content.")

if __name__ == "__main__":
    print("Starting AIO Components Structure Demo...")
    print(f"AIO Components Available: {AIO_AVAILABLE}")
    if AIO_AVAILABLE:
        print("All components loaded successfully!")
        print("Available datasets:", list(SAMPLE_DATA.keys()))
    else:
        print("AIO components not available - showing fallback layout")
    
    app.run_server(debug=True, port=8055)