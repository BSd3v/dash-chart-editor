"""Standalone chart editor backed by dash-pydantic-form."""

from __future__ import annotations

import json
import re
import uuid
from typing import Annotated, Any, Dict, List, Literal, Optional, Set

import dash
from dash import dcc, html, callback, Output, Input, State, MATCH
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
from pydantic import BaseModel, Field, create_model

from dash_pydantic_form import ModelForm

from .px_metadata import PX_CHART_METADATA, NUMERIC_CONSTRAINTS

_PYDF_FORM_ID = "pydantic-chart-editor-form"
_PYDF_LAYOUT_FORM_ID = "pydantic-chart-layout-form"


def _apply_relayout(fig: go.Figure, relayout_data: dict) -> None:
    """Apply user in-graph edits (from relayoutData) back onto a freshly rendered figure.

    Plotly's relayoutData contains key-value pairs using dot-notation for nested layout
    properties (e.g. ``"xaxis.title.text": "my label"``, ``"title.text": "My Chart"``).
    This helper maps those back onto the figure so that user edits survive a chart re-render.

    Note: ``autosize``, ``dragmode``, and zoom/pan viewport keys are intentionally skipped
    because they reflect transient interaction state rather than intentional content edits.
    """
    _SKIP_PREFIXES = ("dragmode", "autosize", "scene")
    _AXIS_RANGE_RE = re.compile(r"^[xy]axis\d*\.range")

    for key, value in relayout_data.items():
        if _AXIS_RANGE_RE.match(key) or any(key.startswith(p) for p in _SKIP_PREFIXES):
            continue
        # Map dot-notation "a.b.c" → nested dict path on layout
        parts = key.split(".")
        target = fig.layout
        try:
            for part in parts[:-1]:
                target = getattr(target, part)
            setattr(target, parts[-1], value)
        except (AttributeError, TypeError):
            pass  # gracefully skip unsupported keys


class _LayoutConfig(BaseModel):
    """Pydantic model for chart layout options."""

    title: Optional[str] = Field(default=None, title="Title")
    height: Optional[int] = Field(default=None, title="Height (px)")
    width: Optional[int] = Field(default=None, title="Width (px)")
    showlegend: Optional[bool] = Field(default=None, title="Show Legend")
    legend_x: Optional[float] = Field(default=None, title="Legend X Position (0–1)")
    legend_y: Optional[float] = Field(default=None, title="Legend Y Position (0–1)")
    legend_orientation: Optional[Literal["v", "h"]] = Field(default=None, title="Legend Orientation")
    legend_xanchor: Optional[Literal["auto", "left", "center", "right"]] = Field(default=None, title="Legend X Anchor")
    legend_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]] = Field(default=None, title="Legend Y Anchor")
    paper_bgcolor: Optional[str] = Field(default=None, title="Paper Background Color")
    plot_bgcolor: Optional[str] = Field(default=None, title="Plot Background Color")


class PydanticChartEditor(html.Div):
    """Standalone chart editor using dash-pydantic-form."""
    _FORM_ID = _PYDF_FORM_ID
    _LAYOUT_FORM_ID = _PYDF_LAYOUT_FORM_ID

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

        @staticmethod
        def excluded_kwargs(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "excluded_kwargs", "aio_id": aio_id}

    def __init__(
        self,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None,
        component_id: Optional[str] = None,
        excluded_kwargs: Optional[Set[str]] = None,
        **kwargs,
    ):
        """Create a PydanticChartEditor component.

        Args:
            data_sources: Named DataFrames to populate column selectors.
            component_id: Unique component identifier. Auto-generated if not provided.
            excluded_kwargs: Set of chart kwarg names to hide from the form.  The developer
                can use this to simplify the editor for their users (e.g. hide ``trendline``,
                ``facet_row``, etc.).
        """
        if component_id is None:
            component_id = str(uuid.uuid4())

        self.component_id = component_id
        self.data_sources = data_sources or {}
        self._serialized_data_sources = {
            name: df.to_dict("records") for name, df in self.data_sources.items()
        }
        self._excluded_kwargs: Set[str] = set(excluded_kwargs or [])

        super().__init__(id=self.ids.container(component_id), children=self._build_layout(), **kwargs)

    @property
    def chart_options(self):
        return [{"label": name, "value": name} for name in sorted(PX_CHART_METADATA.keys())]

    def _build_layout(self):
        option_values = [item["value"] for item in self.chart_options]
        default_chart = "scatter" if "scatter" in option_values else (option_values[0] if option_values else None)
        data_source_options = [{"label": name, "value": name} for name in self.data_sources]
        default_data = data_source_options[0]["value"] if data_source_options else None

        return [
            dmc.MantineProvider(
                html.Div(
                    [
                        html.H4("Chart Editor", style={"marginBottom": "20px"}),
                        html.Label("Chart Type"),
                        dcc.Dropdown(
                            id=self.ids.chart_type(self.component_id),
                            options=self.chart_options,
                            value=default_chart,
                            clearable=False,
                        ),
                        html.Label("Data Source", style={"marginTop": "12px"}),
                        dcc.Dropdown(
                            id=self.ids.data_source(self.component_id),
                            options=data_source_options,
                            value=default_data,
                            clearable=False,
                        ),
                        html.Hr(style={"margin": "16px 0"}),
                        html.H6("Chart Properties", style={"marginBottom": "8px"}),
                        html.Div(id=self.ids.form_container(self.component_id)),
                        html.Hr(style={"margin": "16px 0"}),
                        html.H6("Layout", style={"marginBottom": "8px"}),
                        # Render layout form in layout (not via callback) so its Store exists on load
                        ModelForm(item=_LayoutConfig, aio_id=self.component_id, form_id=_PYDF_LAYOUT_FORM_ID),
                    ],
                    style={"width": "35%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
                )
            ),
            html.Div(
                [
                    dcc.Graph(
                        id=self.ids.chart(self.component_id),
                        style={"height": "600px"},
                        config={
                            "editable": True,       # allow in-chart title/axis/annotation editing
                            "displayModeBar": True,
                        },
                    ),
                    html.Pre(
                        id=self.ids.debug(self.component_id),
                        style={"whiteSpace": "pre-wrap", "fontSize": "12px", "color": "#666"},
                    ),
                    dcc.Store(id=self.ids.data_sources(self.component_id), data=self._serialized_data_sources),
                    dcc.Store(
                        id=self.ids.excluded_kwargs(self.component_id),
                        data=list(self._excluded_kwargs),
                    ),
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
    def _to_figure(chart_type: str, data_frame: pd.DataFrame, chart_kwargs: dict[str, Any]) -> go.Figure:
        chart_fn = getattr(px, chart_type)
        clean_kwargs = {k: v for k, v in chart_kwargs.items() if v not in (None, "")}
        return chart_fn(data_frame=data_frame, **clean_kwargs)

    @staticmethod
    def _build_form_model(chart_type: str, columns: List[str], excluded: Set[str]) -> type[BaseModel]:
        metadata = PX_CHART_METADATA[chart_type]
        column_kwargs = set(metadata["column_kwargs"])
        multi_column_kwargs = set(metadata["multi_column_kwargs"])
        fixed_options: dict[str, list[str]] = metadata.get("fixed_options", {})
        param_defaults: dict[str, Any] = metadata.get("param_defaults", {})

        fields: dict[str, tuple[Any, Any]] = {}
        literal_columns = tuple(columns)

        for arg in metadata["kwargs"]:
            if arg in excluded:
                continue

            title = arg.replace("_", " ").title()
            sig_default = param_defaults.get(arg)

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

            # Fixed options → use Literal so ModelForm renders a Select dropdown.
            # Pre-select the signature default if it appears in the valid options.
            if arg in fixed_options:
                opts = tuple(dict.fromkeys(fixed_options[arg]))  # preserve unique values in original order
                if opts:
                    field_type = Optional[Literal[opts]]  # type: ignore[valid-type]
                    # Use the signature default when it's a valid option; otherwise None
                    field_default = sig_default if isinstance(sig_default, str) and sig_default in opts else None
                    fields[arg] = (field_type, Field(default=field_default, title=title))
                    continue

            # Numeric params: use Annotated types with ge/le constraints so ModelForm
            # renders proper number inputs instead of a plain text box.
            if arg in NUMERIC_CONSTRAINTS:
                nc = NUMERIC_CONSTRAINTS[arg]
                num_type = nc["type"]
                field_kwargs: dict[str, Any] = {"title": title}
                if "ge" in nc:
                    field_kwargs["ge"] = nc["ge"]
                if "le" in nc:
                    field_kwargs["le"] = nc["le"]
                # Exclude bool: in Python bool is a subclass of int, so isinstance(True, int) is True.
                # We never want a boolean signature default to be used as a numeric default here.
                num_default = sig_default if isinstance(sig_default, (int, float)) and not isinstance(sig_default, bool) else None
                fields[arg] = (Optional[num_type], Field(default=num_default, **field_kwargs))
                continue

            inferred = metadata["arg_types"].get(arg, str)
            if inferred in (bool, int, float, dict, list, str):
                field_type = Optional[inferred]
            else:
                field_type = Optional[str]
            fields[arg] = (field_type, Field(default=None, title=title))

        return create_model(f"{chart_type.title()}Form", **fields)

    # ── Auto-wired AIO callbacks ──────────────────────────────────────────────

    @staticmethod
    @callback(
        Output(ids.form_container(MATCH), "children"),
        Input(ids.chart_type(MATCH), "value"),
        Input(ids.data_source(MATCH), "value"),
        State(ids.data_sources(MATCH), "data"),
        State(ids.excluded_kwargs(MATCH), "data"),
        State(ids.form_container(MATCH), "id"),
    )
    def render_form(chart_type, data_source, serialized_data_sources, excluded_kwargs, form_container_id):
        if not chart_type:
            return "Select a chart type to begin."

        records = (serialized_data_sources or {}).get(data_source, [])
        df = pd.DataFrame(records) if records else None
        columns = list(df.columns) if isinstance(df, pd.DataFrame) else []
        aio_id = form_container_id["aio_id"]
        excluded = set(excluded_kwargs or [])

        model = PydanticChartEditor._build_form_model(chart_type, columns, excluded)
        return ModelForm(item=model, aio_id=aio_id, form_id=PydanticChartEditor._FORM_ID)

    @staticmethod
    @callback(
        Output(ids.chart(MATCH), "figure"),
        Output(ids.debug(MATCH), "children"),
        Input(ModelForm.ids.main(MATCH, _PYDF_LAYOUT_FORM_ID), "data"),
        State(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data", allow_optional=True),
        State(ids.chart_type(MATCH), "value"),
        State(ids.data_source(MATCH), "value"),
        State(ids.data_sources(MATCH), "data"),
        State(ids.chart(MATCH), "relayoutData"),
        prevent_initial_call=True,
    )
    def update_chart_from_layout(layout_data, form_data, chart_type, data_source, serialized_data_sources, relayout_data):
        return PydanticChartEditor._render_chart(
            form_data, layout_data, chart_type, data_source, serialized_data_sources, relayout_data
        )

    @staticmethod
    @callback(
        Output(ids.chart(MATCH), "figure", allow_duplicate=True),
        Output(ids.debug(MATCH), "children", allow_duplicate=True),
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        State(ModelForm.ids.main(MATCH, _PYDF_LAYOUT_FORM_ID), "data"),
        State(ids.chart_type(MATCH), "value"),
        State(ids.data_source(MATCH), "value"),
        State(ids.data_sources(MATCH), "data"),
        State(ids.chart(MATCH), "relayoutData"),
        prevent_initial_call=True,
    )
    def update_chart(form_data, layout_data, chart_type, data_source, serialized_data_sources, relayout_data):
        return PydanticChartEditor._render_chart(
            form_data, layout_data, chart_type, data_source, serialized_data_sources, relayout_data
        )

    @staticmethod
    def _render_chart(form_data, layout_data, chart_type, data_source, serialized_data_sources, relayout_data=None):
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
            return go.Figure(), "Select a column for this chart type to render."

        try:
            fig = PydanticChartEditor._to_figure(chart_type=chart_type, data_frame=df, chart_kwargs=parsed)

            # Apply pydantic layout panel settings
            layout_cfg = layout_data or {}
            legend_update: dict[str, Any] = {}
            layout_update: dict[str, Any] = {}
            for key, val in layout_cfg.items():
                if val is None:
                    continue
                if key.startswith("legend_"):
                    legend_update[key[len("legend_"):]] = val
                else:
                    layout_update[key] = val

            if legend_update:
                layout_update["legend"] = legend_update
            if layout_update:
                fig.update_layout(**layout_update)

            # Re-apply any in-graph user edits (title, axis labels, annotations, etc.)
            # relayoutData contains only the delta of changes made by the user in the graph.
            if relayout_data:
                _apply_relayout(fig, relayout_data)

            return fig, json.dumps({"chart_type": chart_type, "kwargs": parsed}, indent=2, default=str)
        except Exception as exc:  # pragma: no cover - UI feedback path
            error = go.Figure()
            error.update_layout(title=f"Error creating {chart_type}: {exc}")
            return error, str(exc)


def create_pydantic_chart_editor_app(
    data_sources: Dict[str, pd.DataFrame],
    port: int = 8054,
    excluded_kwargs: Optional[Set[str]] = None,
):
    app = dash.Dash(__name__)
    editor = PydanticChartEditor(
        data_sources=data_sources,
        component_id="main-editor",
        excluded_kwargs=excluded_kwargs,
    )

    app.layout = html.Div([
        html.H1("Pydantic Chart Editor", style={"textAlign": "center", "marginBottom": "20px"}),
        editor,
    ])

    return app
