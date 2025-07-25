"""
DCC Chart Editor Example Page

Standalone example demonstrating the DCCChartEditor component
using only standard Dash DCC components.
"""

import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px

# Import the DCC chart editor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_chart_editor.aio.dcc_chart_editor import create_dcc_chart_editor_app

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
app = create_dcc_chart_editor_app(data_sources, port=8055)

if __name__ == "__main__":
    print("Starting DCC Chart Editor on http://localhost:8055")
    app.run(debug=True, port=8055)