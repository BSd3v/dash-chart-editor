"""
AIO Multi-Chart Editor Example

Demonstrates the usage of MultiChartEditorAIO component with chart management capabilities.
"""

import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px

# Import the AIO components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_chart_editor.aio import MultiChartEditorAIO

# Sample datasets
iris_df = px.data.iris()
tips_df = px.data.tips()
gapminder_df = px.data.gapminder()

data_sources = {
    'Iris Dataset': iris_df,
    'Tips Dataset': tips_df,
    'Gapminder Dataset': gapminder_df
}

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
])

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([
        html.H1("Multi-Chart Editor AIO Example", className="text-center mb-4"),
        html.P("This example demonstrates the MultiChartEditorAIO component for managing multiple charts.", 
               className="text-center text-muted"),
        html.Hr()
    ], className="container-fluid bg-light py-3 mb-4"),
    
    html.Div([
        MultiChartEditorAIO(
            data_sources=data_sources,
            aio_id="multi-editor",
            flavor="dcc"
        )
    ], className="container-fluid"),
    
    # Store for data access in callbacks
    dcc.Store(id="data-store", data={
        name: df.to_dict('records') for name, df in data_sources.items()
    })
])

if __name__ == "__main__":
    app.run(debug=True, port=8052)