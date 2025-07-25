"""
Pydantic Chart Editor Example Page

Standalone example demonstrating the PydanticChartEditor component
using dash-pydantic-form with dynamic chart-specific parameters.
"""

import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px

try:
    from dash_pydantic_form import ModelForm
    PYDANTIC_FORM_AVAILABLE = True
except ImportError:
    PYDANTIC_FORM_AVAILABLE = False
    print("Warning: dash_pydantic_form not available. Install with: pip install dash-pydantic-form")

if PYDANTIC_FORM_AVAILABLE:
    # Import the Pydantic chart editor
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from dash_chart_editor.aio.pydantic_chart_editor import create_pydantic_chart_editor_app

    # Sample datasets
    iris_df = px.data.iris()
    tips_df = px.data.tips()
    stocks_df = px.data.stocks()
    gapminder_df = px.data.gapminder()

    data_sources = {
        'Iris Dataset': iris_df,
        'Tips Dataset': tips_df,
        'Stocks Dataset': stocks_df,
        'Gapminder Dataset': gapminder_df
    }

    # Create the app
    app = create_pydantic_chart_editor_app(data_sources, port=8054)

    if __name__ == "__main__":
        print("Starting Pydantic Chart Editor on http://localhost:8054")
        app.run(debug=True, port=8054)

else:
    # Fallback app when pydantic form is not available
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.Div([
            html.H1("Dash Pydantic Form Not Available", style={'color': 'red'}),
            html.P("Please install dash-pydantic-form to run this example:"),
            html.Code("pip install dash-pydantic-form", style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'display': 'block', 'margin': '20px 0'}),
            html.Br(),
            html.P([
                "Or run the DCC flavor example instead: ",
                html.A("DCC Chart Editor", href="http://localhost:8055", target="_blank")
            ])
        ], style={'textAlign': 'center', 'padding': '50px', 'fontFamily': 'Arial'})
    ])

    if __name__ == "__main__":
        print("dash-pydantic-form not available. Starting fallback app on http://localhost:8054")
        app.run(debug=True, port=8054)