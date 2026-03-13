"""Standalone chart editor backed by dash-pydantic-form."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Literal, Optional

import dash
from dash import dcc, html, callback, Output, Input, State, MATCH
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
from pydantic import BaseModel, Field, create_model

from dash_pydantic_form import ModelForm

from .px_metadata import PX_CHART_METADATA

_PYDF_FORM_ID = "pydantic-chart-editor-form"


class PydanticChartEditor(html.Div):
    """Standalone chart editor using dash-pydantic-form."""
    _FORM_ID = _PYDF_FORM_ID

    class ids:
        @staticmethod
        def container(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "container", "aio_id": aio_id}

        @staticmethod
        def chart_type(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "chart_type", "aio_id": aio_id}

        @staticmethod
        def data_source(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "data_source", "aio_id": aio_id}

        @staticmethod
        def form_container(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "form_container", "aio_id": aio_id}

        @staticmethod
        def chart(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "chart", "aio_id": aio_id}

        @staticmethod
        def debug(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "debug", "aio_id": aio_id}

        @staticmethod
        def data_sources(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "data_sources", "aio_id": aio_id}

    def __init__(self, data_sources: Optional[Dict[str, pd.DataFrame]] = None, component_id: Optional[str] = None, **kwargs):
        if component_id is None:
            component_id = str(uuid.uuid4())

        self.component_id = component_id
        self.data_sources = data_sources or {}
        self._serialized_data_sources = {
            name: df.to_dict("records") for name, df in self.data_sources.items()
        }

        super().__init__(id=self.ids.container(component_id), children=self._build_layout(), **kwargs)

    @property
    def chart_options(self):
        return [{"label": name, "value": name} for name in sorted(PX_CHART_METADATA.keys())]

    def _build_layout(self):
        option_values = [item["value"] for item in self.chart_options]
        default_chart = "scatter" if "scatter" in option_values else (option_values[0] if option_values else None)
        data_sources = [{"label": name, "value": name} for name in self.data_sources]
        default_data = data_sources[0]["value"] if data_sources else None

        return [
            dmc.MantineProvider(
                html.Div(
                [
                    html.H4("Pydantic Chart Editor", style={"marginBottom": "20px"}),
                    html.Label("Chart Type"),
                    dcc.Dropdown(id=self.ids.chart_type(self.component_id), options=self.chart_options, value=default_chart, clearable=False),
                    html.Label("Data Source", style={"marginTop": "12px"}),
                    dcc.Dropdown(id=self.ids.data_source(self.component_id), options=data_sources, value=default_data, clearable=False),
                    html.Div(id=self.ids.form_container(self.component_id), style={"marginTop": "12px"}),
                ],
                style={"width": "35%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
                )
            ),
            html.Div(
                [
                    dcc.Graph(id=self.ids.chart(self.component_id), style={"height": "600px"}),
                    html.Pre(id=self.ids.debug(self.component_id), style={"whiteSpace": "pre-wrap", "fontSize": "12px", "color": "#666"}),
                    dcc.Store(id=self.ids.data_sources(self.component_id), data=self._serialized_data_sources),
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

    @staticmethod
    def _build_form_model(chart_type: str, columns: List[str]) -> type[BaseModel]:
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

    @staticmethod
    @callback(
        Output(ids.form_container(MATCH), "children"),
        Input(ids.chart_type(MATCH), "value"),
        Input(ids.data_source(MATCH), "value"),
        State(ids.data_sources(MATCH), "data"),
        State(ids.form_container(MATCH), "id"),
    )
    def render_form(chart_type, data_source, serialized_data_sources, form_container_id):
        if not chart_type:
            return "Select a chart type to begin."

        records = (serialized_data_sources or {}).get(data_source, [])
        df = pd.DataFrame(records) if records else None
        columns = list(df.columns) if isinstance(df, pd.DataFrame) else []
        aio_id = form_container_id["aio_id"]

        model = PydanticChartEditor._build_form_model(chart_type, columns)
        return ModelForm(item=model, aio_id=aio_id, form_id=PydanticChartEditor._FORM_ID)

    @staticmethod
    @callback(
        Output(ids.chart(MATCH), "figure"),
        Output(ids.debug(MATCH), "children"),
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        State(ids.chart_type(MATCH), "value"),
        State(ids.data_source(MATCH), "value"),
        State(ids.data_sources(MATCH), "data"),
        prevent_initial_call=True,
    )
    def update_chart(form_data, chart_type, data_source, serialized_data_sources):
        if not chart_type or not data_source:
            return go.Figure(), "Select chart type and data source."

        records = (serialized_data_sources or {}).get(data_source, [])
        if not records:
            return go.Figure(), f"Unknown data source: {data_source}"
        df = pd.DataFrame(records)

        metadata = PX_CHART_METADATA.get(chart_type, {})
        kwarg_names = metadata.get("kwargs", [])
        column_candidates = set(metadata.get("column_kwargs", [])) | set(metadata.get("multi_column_kwargs", []))

        parsed = {
            key: PydanticChartEditor._parse_scalar_value(value)
            for key, value in (form_data or {}).items()
            if key in kwarg_names
        }
        has_column_selection = any(parsed.get(name) not in (None, "", []) for name in column_candidates)

        if not has_column_selection:
            placeholder = go.Figure()
            placeholder.update_layout(title=f"Select at least one column option for {chart_type}.")
            return placeholder, "Waiting for column selection..."

        try:
            fig = PydanticChartEditor._to_figure(chart_type=chart_type, data_frame=df, kwargs=parsed)
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

    return app
