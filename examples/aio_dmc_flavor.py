"""
AIO Chart Editor with DMC Flavor Example

Demonstrates the usage of ChartEditorAIO component with Dash Mantine Components (DMC) flavor.
"""

import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    import dash_mantine_components as dmc
    DMC_AVAILABLE = True
except ImportError:
    DMC_AVAILABLE = False
    print("Warning: dash_mantine_components not available. Install with: pip install dash-mantine-components")

# Import the AIO components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_chart_editor.aio import ChartEditorAIO

# Sample datasets
iris_df = px.data.iris()
tips_df = px.data.tips()
stocks_df = px.data.stocks()

data_sources = {
    'Iris Dataset': iris_df,
    'Tips Dataset': tips_df,
    'Stocks Dataset': stocks_df
}

# Initialize the Dash app
app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

if DMC_AVAILABLE:
    app.layout = dmc.MantineProvider([
        dmc.Container([
            dmc.Header([
                dmc.Title("Chart Editor AIO - DMC Flavor Example", order=1, align="center"),
                dmc.Text("This example demonstrates the ChartEditorAIO component using Dash Mantine Components.", 
                        align="center", color="dimmed", size="lg")
            ], height=120, p="md", style={"backgroundColor": "#f8f9fa"}),
            
            dmc.Space(h="md"),
            
            ChartEditorAIO(
                data_sources=data_sources,
                aio_id="dmc-editor",
                flavor="dmc"
            ),
            
            # Store for data access in callbacks
            dcc.Store(id="data-store", data={
                name: df.to_dict('records') for name, df in data_sources.items()
            })
        ], fluid=True)
    ])
    
    # Custom callback to handle chart updates with actual data
    @callback(
        [
            Output({"component": "ChartEditorAIO", "subcomponent": "chart", "aio_id": "dmc-editor"}, "figure"),
            Output({"component": "ChartEditorAIO", "subcomponent": "figure_data", "aio_id": "dmc-editor"}, "children"),
        ],
        [
            Input({"component": "ChartEditorAIO", "subcomponent": "chart_type", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "x_column", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "y_column", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "color_column", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "size_column", "aio_id": "dmc-editor"}, "value"),
            Input({"component": "ChartEditorAIO", "subcomponent": "title", "aio_id": "dmc-editor"}, "value"),
        ],
        Input("data-store", "data"),
        prevent_initial_call=True
    )
    def update_chart_with_data(chart_type, data_source, x_col, y_col, color_col, size_col, title, stored_data):
        """Update chart with actual data from the selected source"""
        
        if not data_source or not x_col or not y_col or data_source not in stored_data:
            fig = go.Figure()
            fig.update_layout(title=title or "Select data and columns to create chart")
            return fig, str(fig.to_dict())
        
        # Convert stored data back to DataFrame
        df = pd.DataFrame(stored_data[data_source])
        
        # Create chart based on type
        try:
            if chart_type == 'scatter':
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
            elif chart_type == 'line':
                fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'bar':
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=x_col, color=color_col, title=title)
            elif chart_type == 'box':
                fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'violin':
                fig = px.violin(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'pie':
                if x_col:
                    fig = px.pie(df, names=x_col, values=y_col, title=title)
                else:
                    fig = go.Figure()
                    fig.update_layout(title="Pie chart requires both name and value columns")
            elif chart_type == 'heatmap':
                # For heatmap, we'll use a correlation matrix if numeric columns are selected
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    corr_df = df[numeric_cols].corr()
                    fig = px.imshow(corr_df, title=title or "Correlation Heatmap")
                else:
                    fig = go.Figure()
                    fig.update_layout(title="Heatmap requires numeric columns")
            else:
                fig = go.Figure()
                fig.update_layout(title="Unsupported chart type")
            
            fig.update_layout(height=500)
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error creating chart: {str(e)}")
        
        return fig, str(fig.to_dict())

    # Callback to update column options when data source changes
    @callback(
        Output(f"column-controls-dmc-editor", "children"),
        Input({"component": "ChartEditorAIO", "subcomponent": "data_source", "aio_id": "dmc-editor"}, "value"),
        Input("data-store", "data"),
        prevent_initial_call=True
    )
    def update_column_options(data_source, stored_data):
        """Update column selection options when data source changes"""
        if not data_source or data_source not in stored_data:
            return dmc.Text("Select a data source to see column options.", color="dimmed")
        
        df = pd.DataFrame(stored_data[data_source])
        columns = df.columns.tolist()
        column_options = [{'label': col, 'value': col} for col in columns]
        
        return dmc.Stack([
            dmc.Select(
                label="X Column",
                data=column_options,
                value=columns[0] if columns else None,
                id={"component": "ChartEditorAIO", "subcomponent": "x_column", "aio_id": "dmc-editor"}
            ),
            dmc.Select(
                label="Y Column",
                data=column_options,
                value=columns[1] if len(columns) > 1 else None,
                id={"component": "ChartEditorAIO", "subcomponent": "y_column", "aio_id": "dmc-editor"}
            ),
            dmc.Select(
                label="Color Column (optional)",
                data=column_options,
                clearable=True,
                id={"component": "ChartEditorAIO", "subcomponent": "color_column", "aio_id": "dmc-editor"}
            ),
            dmc.Select(
                label="Size Column (optional)",
                data=column_options,
                clearable=True,
                id={"component": "ChartEditorAIO", "subcomponent": "size_column", "aio_id": "dmc-editor"}
            )
        ])

else:
    # Fallback layout when DMC is not available
    app.layout = html.Div([
        html.H1("DMC Not Available"),
        html.P("Please install dash-mantine-components to run this example:"),
        html.Code("pip install dash-mantine-components"),
        html.Br(),
        html.A("Run the DCC flavor example instead", href="/examples/aio_single_chart.py")
    ], style={'textAlign': 'center', 'padding': '50px'})

if __name__ == "__main__":
    app.run_server(debug=True, port=8053)