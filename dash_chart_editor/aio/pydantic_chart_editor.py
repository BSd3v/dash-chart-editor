"""Standalone chart editor backed by dash-pydantic-form."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Literal, Optional

import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pydantic import BaseModel, Field, create_model

from dash_pydantic_form import ModelForm

from .px_metadata import PX_CHART_METADATA


class PydanticChartEditor(html.Div):
    """Standalone chart editor using dash-pydantic-form."""

    def __init__(self, data_sources: Optional[Dict[str, pd.DataFrame]] = None, component_id: Optional[str] = None, **kwargs):
        if component_id is None:
            component_id = str(uuid.uuid4())

        self.component_id = component_id
        self.data_sources = data_sources or {}
        self._form_id = f"pydantic-chart-editor-form-{component_id}"

        super().__init__(id=f"pydantic-chart-editor-{component_id}", children=self._build_layout(), **kwargs)

    @property
    def chart_options(self):
        return [{"label": name, "value": name} for name in sorted(PX_CHART_METADATA.keys())]

    def _build_layout(self):
        default_chart = self.chart_options[0]["value"] if self.chart_options else None
        data_sources = [{"label": name, "value": name} for name in self.data_sources]
        default_data = data_sources[0]["value"] if data_sources else None

        return [
            html.Div(
                [
                    html.H4("Pydantic Chart Editor", style={"marginBottom": "20px"}),
                    html.Label("Chart Type"),
                    dcc.Dropdown(id=f"chart-type-{self.component_id}", options=self.chart_options, value=default_chart, clearable=False),
                    html.Label("Data Source", style={"marginTop": "12px"}),
                    dcc.Dropdown(id=f"data-source-{self.component_id}", options=data_sources, value=default_data, clearable=False),
                    html.Div(id=f"form-container-{self.component_id}", style={"marginTop": "12px"}),
                ],
                style={"width": "35%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
            ),
            html.Div(
                [
                    dcc.Graph(id=f"chart-{self.component_id}", style={"height": "600px"}),
                    html.Pre(id=f"debug-{self.component_id}", style={"whiteSpace": "pre-wrap", "fontSize": "12px", "color": "#666"}),
                ],
                style={"width": "63%", "display": "inline-block", "marginLeft": "2%"},
            ),
        ]

    @staticmethod
    def _parse_scalar_value(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        text = value.strip()
        if not text:
            return None
        if text.lower() in {"true", "false"}:
            return text.lower() == "true"
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return value

    @staticmethod
    def _to_figure(chart_type: str, data_frame: pd.DataFrame, kwargs: dict[str, Any]) -> go.Figure:
        chart_fn = getattr(px, chart_type)
        clean_kwargs = {k: v for k, v in kwargs.items() if v not in (None, "")}
        return chart_fn(data_frame=data_frame, **clean_kwargs)

    def _build_form_model(self, chart_type: str, columns: List[str]) -> type[BaseModel]:
        metadata = PX_CHART_METADATA[chart_type]
        column_kwargs = set(metadata["column_kwargs"])
        multi_column_kwargs = set(metadata["multi_column_kwargs"])

        fields: dict[str, tuple[Any, Any]] = {}
        literal_columns = tuple(columns)

        for arg in metadata["kwargs"]:
            title = arg.replace("_", " ").title()

            if arg in multi_column_kwargs:
                if literal_columns:
                    field_type = Optional[List[Literal[literal_columns]]]  # type: ignore[valid-type]
                else:
                    field_type = Optional[List[str]]
                fields[arg] = (field_type, Field(default=None, title=title))
                continue

            if arg in column_kwargs:
                if literal_columns:
                    field_type = Optional[Literal[literal_columns]]  # type: ignore[valid-type]
                else:
                    field_type = Optional[str]
                fields[arg] = (field_type, Field(default=None, title=title))
                continue

            inferred = metadata["arg_types"].get(arg, str)
            if inferred in (bool, int, float, dict, list, str):
                field_type = Optional[inferred]
            else:
                field_type = Optional[str]
            fields[arg] = (field_type, Field(default=None, title=title))

        return create_model(f"{chart_type.title()}Form", **fields)

    def register_callbacks(self, app):
        @app.callback(
            dash.Output(f"form-container-{self.component_id}", "children"),
            dash.Input(f"chart-type-{self.component_id}", "value"),
            dash.Input(f"data-source-{self.component_id}", "value"),
        )
        def render_form(chart_type, data_source):
            if not chart_type:
                return "Select a chart type to begin."

            df = self.data_sources.get(data_source)
            columns = list(df.columns) if isinstance(df, pd.DataFrame) else []
            model = self._build_form_model(chart_type, columns)

            return ModelForm(item=model, aio_id=self.component_id, form_id=self._form_id)

        @app.callback(
            dash.Output(f"chart-{self.component_id}", "figure"),
            dash.Output(f"debug-{self.component_id}", "children"),
            dash.Input(ModelForm.ids.main(self.component_id, self._form_id), "data"),
            dash.State(f"chart-type-{self.component_id}", "value"),
            dash.State(f"data-source-{self.component_id}", "value"),
            prevent_initial_call=True,
        )
        def update_chart(form_data, chart_type, data_source):
            if not chart_type or not data_source:
                return go.Figure(), "Select chart type and data source."

            df = self.data_sources.get(data_source)
            if df is None:
                return go.Figure(), f"Unknown data source: {data_source}"

            metadata = PX_CHART_METADATA.get(chart_type, {})
            kwarg_names = metadata.get("kwargs", [])

            parsed = {
                key: self._parse_scalar_value(value)
                for key, value in (form_data or {}).items()
                if key in kwarg_names
            }

            try:
                fig = self._to_figure(chart_type=chart_type, data_frame=df, kwargs=parsed)
                return fig, json.dumps({"chart_type": chart_type, "kwargs": parsed}, indent=2, default=str)
            except Exception as exc:  # pragma: no cover - UI feedback path
                error = go.Figure()
                error.update_layout(title=f"Error creating {chart_type}: {exc}")
                return error, str(exc)


def create_pydantic_chart_editor_app(data_sources: Dict[str, pd.DataFrame], port: int = 8054):
    app = dash.Dash(__name__)
    editor = PydanticChartEditor(data_sources=data_sources, component_id="main-editor")

    app.layout = html.Div([
        html.H1("Pydantic Chart Editor", style={"textAlign": "center", "marginBottom": "20px"}),
        editor,
    ])

    editor.register_callbacks(app)
    return app
