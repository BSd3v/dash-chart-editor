
import dash
import dash_mantine_components as dmc
from dash import html
import pandas as pd
from dash_chart_editor.aio.pydantic_chart_editor import PydanticChartEditorAIO

# Sample data
df = pd.DataFrame({
    "A": [1, 2, 3, 4],
    "B": [10, 20, 30, 40],
    "C": [5, 6, 7, 8]
})

# Register data sources globally for the AIO
PydanticChartEditorAIO._data_sources = {"Sample Data": df}

# Create the Dash app
app = dash.Dash(__name__)

# Instantiate the AIO component
editor = PydanticChartEditorAIO(aio_id="demo", data_sources=PydanticChartEditorAIO._data_sources)

# App layout
app.layout = dmc.MantineProvider([
    html.H2("Pydantic Chart Editor Demo"),
    editor.layout()
])

if __name__ == "__main__":
    app.run(debug=True)