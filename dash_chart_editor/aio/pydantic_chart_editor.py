"""Standalone chart editor backed by dash-pydantic-form.

Charts section uses a pydantic-form list to manage multiple chart entries.
All charts share a single dcc.Graph and a common layout configuration.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Literal, Optional, Set, Union

import dash
from dash import dcc, html, callback, Output, Input, State, MATCH, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
from pydantic import BaseModel, Field, create_model
from pydantic import ValidationError

from dash_pydantic_form import ModelForm, AccordionFormLayout, FormSection

from .px_metadata import PX_CHART_METADATA, NUMERIC_CONSTRAINTS

_PYDF_FORM_ID = "pydantic-chart-editor-form"

# All chart type names available from Plotly Express metadata.
_CHART_TYPES: tuple = tuple(sorted(PX_CHART_METADATA.keys()))

# Maps Plotly relayoutData keys → _LayoutConfig field names.
# Used by sync_relayout_to_form to keep the layout form in step when the user
# edits the chart directly (click-to-edit title, drag legend, etc.).
_RELAYOUT_TO_LAYOUT: dict = {
    "title.text": "title",
    "showlegend": "showlegend",
    "legend.x": "legend_x",
    "legend.y": "legend_y",
    "legend.orientation": "legend_orientation",
    "legend.xanchor": "legend_xanchor",
    "legend.yanchor": "legend_yanchor",
    "paper_bgcolor": "paper_bgcolor",
    "plot_bgcolor": "plot_bgcolor",
    "width": "width",
    "height": "height",
}

# Plotly Express API reference URL pattern for doc links.
_PX_API_BASE = "https://plotly.com/python-api-reference/generated/plotly.express.{}.html"
_PX_EXAMPLES_URL = "https://plotly.com/python/"
_LAYOUT_REF_URL = (
    "https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html"
)

# Maximum length for field descriptions/tooltips sourced from Plotly docstrings.
# Re-exported so external tests and tooling can use the same constant.
MAX_DESCRIPTION_LENGTH = 200


def _apply_relayout(fig: go.Figure, relayout_data: dict) -> None:
    """Apply user in-graph edits (from relayoutData) back onto a freshly rendered figure.

    Plotly's relayoutData contains key-value pairs using dot-notation for nested layout
    properties (e.g. ``"xaxis.title.text": "my label"``).  Transient interaction keys
    (drag-mode, autosize, zoom/pan ranges) are intentionally skipped.
    """
    _SKIP_PREFIXES = ("dragmode", "autosize", "scene")
    _AXIS_RANGE_RE = re.compile(r"^[xy]axis\d*\.range")

    for key, value in relayout_data.items():
        if _AXIS_RANGE_RE.match(key) or any(key.startswith(p) for p in _SKIP_PREFIXES):
            continue
        parts = key.split(".")
        target = fig.layout
        try:
            for part in parts[:-1]:
                target = getattr(target, part)
            setattr(target, parts[-1], value)
        except (AttributeError, TypeError):
            pass


class _LayoutConfig(BaseModel):
    """Shared layout options applied across all charts in the same figure."""

    title: Optional[str] = Field(default=None, title="Title",
                                  description="The chart title displayed above the plot.")
    height: Optional[int] = Field(default=None, title="Height (px)",
                                   description="Height of the figure in pixels.", ge=100)
    width: Optional[int] = Field(default=None, title="Width (px)",
                                  description="Width of the figure in pixels.", ge=100)
    showlegend: Optional[bool] = Field(default=None, title="Show Legend",
                                        description="Whether to display the legend.")
    legend_x: Optional[float] = Field(default=None, title="Legend X Position (0–1)",
                                       description="Horizontal position of the legend (0=left, 1=right).",
                                       ge=0.0, le=1.0, multiple_of=0.1)
    legend_y: Optional[float] = Field(default=None, title="Legend Y Position (0–1)",
                                       description="Vertical position of the legend (0=bottom, 1=top).",
                                       ge=0.0, le=1.0, multiple_of=0.1)
    legend_orientation: Optional[Literal["v", "h"]] = Field(
        default=None, title="Legend Orientation",
        description="'v' for vertical, 'h' for horizontal.")
    legend_xanchor: Optional[Literal["auto", "left", "center", "right"]] = Field(
        default=None, title="Legend X Anchor",
        description="Horizontal anchor point for the legend position.")
    legend_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]] = Field(
        default=None, title="Legend Y Anchor",
        description="Vertical anchor point for the legend position.")
    paper_bgcolor: Optional[str] = Field(default=None, title="Paper Background Color",
                                          description="Background color of the full figure area.")
    plot_bgcolor: Optional[str] = Field(default=None, title="Plot Background Color",
                                         description="Background color of the plot area.")
    template: Optional[str] = Field(default=None, title="Template",
                                    description="Plotly template for chart styling.")


class _ChartEntry(BaseModel):
    """Configuration for a single chart trace in the multi-chart editor."""

    label: str = Field(default="Chart", title="Label",
                       description="Name for this trace shown in the legend.")
    chart_type: Optional[Literal[_CHART_TYPES]] = Field(  # type: ignore[valid-type]
        default="scatter", title="Chart Type",
        description="Plotly Express chart function to use for this trace.")
    data_source: Optional[str] = Field(
        default=None, title="Data Source",
        description="Dataset name — must match a key in data_sources passed to PydanticChartEditor.")
    x: Optional[str] = Field(default=None, title="X",
                              description="Column name for the X axis.")
    y: Optional[str] = Field(default=None, title="Y",
                              description="Column name for the Y axis.")
    color: Optional[str] = Field(default=None, title="Color",
                                  description="Column name for color encoding.")
    size: Optional[str] = Field(default=None, title="Size",
                                 description="Column name for marker size (scatter / bubble).")
    names: Optional[str] = Field(default=None, title="Names",
                                  description="Column name for category labels (pie / funnel).")
    values: Optional[str] = Field(default=None, title="Values",
                                   description="Column name for numeric values (pie / funnel).")
    opacity: Optional[float] = Field(default=None, title="Opacity",
                                       description="Marker opacity between 0 (transparent) and 1 (opaque).",
                                       ge=0.0, le=1.0, multiple_of=0.1)


_DYNAMIC_CHART_MODELS: Optional[List[type[BaseModel]]] = None
_DYNAMIC_CHART_UNION: Optional[Any] = None
_DYNAMIC_EDITOR_STATE_MODEL: Optional[type[BaseModel]] = None


def _build_dynamic_chart_model(chart_type: str, metadata: dict) -> type[BaseModel]:
    """Build a chart-entry model for a specific Plotly Express chart type."""
    fields: Dict[str, Any] = {
        "label": (str, Field(default="Chart", title="Label")),
        "chart_type": (Literal[chart_type], Field(default=chart_type, title="Chart Type")),  # type: ignore[valid-type]
        "data_source": (Optional[str], Field(default=None, title="Data Source")),
    }

    fixed_options: dict = metadata.get("fixed_options", {})
    param_defaults: dict = metadata.get("param_defaults", {})
    param_descriptions: dict = metadata.get("param_descriptions", {})
    column_kwargs = set(metadata.get("column_kwargs", []))
    multi_column_kwargs = set(metadata.get("multi_column_kwargs", []))

    for arg in metadata.get("kwargs", []):
        title = arg.replace("_", " ").title()
        desc = param_descriptions.get(arg, "")
        sig_default = param_defaults.get(arg)

        if arg in multi_column_kwargs:
            fields[arg] = (
                Optional[List[str]],
                Field(default=None, title=title, description=desc or None),
            )
            continue

        if arg in column_kwargs:
            fields[arg] = (
                Optional[str],
                Field(default=None, title=title, description=desc or None),
            )
            continue

        if arg in fixed_options:
            opts = tuple(dict.fromkeys(fixed_options[arg]))
            if opts:
                field_type = Optional[Literal[opts]]  # type: ignore[valid-type]
                field_default = sig_default if isinstance(sig_default, str) and sig_default in opts else None
                fields[arg] = (
                    field_type,
                    Field(default=field_default, title=title, description=desc or None),
                )
                continue

        if arg in NUMERIC_CONSTRAINTS:
            nc = NUMERIC_CONSTRAINTS[arg]
            field_kwargs: dict = {"title": title}
            if desc:
                field_kwargs["description"] = desc
            if "ge" in nc:
                field_kwargs["ge"] = nc["ge"]
            if "le" in nc:
                field_kwargs["le"] = nc["le"]
            if "multiple_of" in nc:
                field_kwargs["multiple_of"] = nc["multiple_of"]
            num_default = (
                sig_default
                if isinstance(sig_default, (int, float)) and not isinstance(sig_default, bool)
                else None
            )
            fields[arg] = (Optional[nc["type"]], Field(default=num_default, **field_kwargs))
            continue

        inferred = metadata.get("arg_types", {}).get(arg, str)
        if inferred in (bool, int, float, dict, list, str):
            field_type = Optional[inferred]
        else:
            field_type = Optional[str]
        fields[arg] = (field_type, Field(default=None, title=title, description=desc or None))

    return create_model(f"{chart_type.title()}ChartEntry", **fields)


def _get_chart_union_models() -> List[type[BaseModel]]:
    """Return list of per-chart models built from currently available px chart metadata."""
    global _DYNAMIC_CHART_MODELS
    if _DYNAMIC_CHART_MODELS is None:
        _DYNAMIC_CHART_MODELS = [
            _build_dynamic_chart_model(chart_type, PX_CHART_METADATA[chart_type])
            for chart_type in sorted(PX_CHART_METADATA.keys())
        ]
    if not _DYNAMIC_CHART_MODELS:
        raise RuntimeError("PX_CHART_METADATA is empty; cannot build chart union models.")
    return _DYNAMIC_CHART_MODELS


def _get_chart_union_type() -> Any:
    """Return Union[...] of all dynamic chart-entry models."""
    global _DYNAMIC_CHART_UNION
    if _DYNAMIC_CHART_UNION is None:
        models = tuple(_get_chart_union_models())
        _DYNAMIC_CHART_UNION = Union[models]
    return _DYNAMIC_CHART_UNION


def _get_editor_state_model() -> type[BaseModel]:
    """Return dynamic editor-state model containing chart union list + shared layout."""
    global _DYNAMIC_EDITOR_STATE_MODEL
    if _DYNAMIC_EDITOR_STATE_MODEL is None:
        chart_union = _get_chart_union_type()
        _DYNAMIC_EDITOR_STATE_MODEL = create_model(
            "_DynamicEditorState",
            charts=(
                List[chart_union],  # type: ignore[valid-type]
                Field(
                    default_factory=list,
                    title="",
                    description=(
                        "Configure individual chart traces as a typed list. "
                        "Add multiple charts to overlay on the same graph."
                    ),
                ),
            ),
            shared_layout=(
                _LayoutConfig,
                Field(
                    default_factory=_LayoutConfig,
                    title="",
                    description="Layout settings shared across all charts in this figure.",
                ),
            ),
        )
    return _DYNAMIC_EDITOR_STATE_MODEL


# Backward-compatible alias used in tests/imports.
_EditorState = _get_editor_state_model()


class PydanticChartEditor(html.Div):
    """Standalone chart editor using dash-pydantic-form.

    The editor renders a ``ModelForm`` for ``_EditorState``, which contains:
    - **Charts** accordion section — a pydantic-form list of ``_ChartEntry`` items,
      each with chart type, data source, and column selectors.  The list supports
      adding and removing charts via pydf's native list UI.
    - **Layout** accordion section — a ``_LayoutConfig`` form for the shared layout
      (title, legend position, background colours, etc.).

    All charts in the list are combined as traces on a single ``dcc.Graph``.
    The shared layout is applied once to the whole figure.
    """

    _FORM_ID = _PYDF_FORM_ID

    class ids:
        @staticmethod
        def container(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "container", "aio_id": aio_id}

        @staticmethod
        def chart(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "chart", "aio_id": aio_id}

        @staticmethod
        def debug(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "debug", "aio_id": aio_id}

        @staticmethod
        def data_sources(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "data_sources", "aio_id": aio_id}

    def __init__(
        self,
        data_sources: Optional[Dict[str, pd.DataFrame]] = None,
        component_id: Optional[str] = None,
        excluded_kwargs: Optional[Set[str]] = None,
        show_doc_link: bool = True,
        multi_chart: bool = True,
        **kwargs,
    ):
        """Create a PydanticChartEditor component.

        Args:
            data_sources: Named DataFrames to populate the data-source field choices.
            component_id: Unique component identifier. Auto-generated if not provided.
            excluded_kwargs: Accepted for backward compatibility; not used in the
                ModelForm-based editor (field visibility is controlled by the model).
            show_doc_link: Retained for backward compatibility.  The doc-links panel
                is no longer per-chart-type in the new layout.
            multi_chart: When ``True`` (default), the Charts accordion section renders
                a pydantic-form list that lets users add / remove chart entries.
                When ``False``, only a single chart entry is shown.
        """
        if component_id is None:
            component_id = str(uuid.uuid4())

        self.component_id = component_id
        self.data_sources = data_sources or {}
        self._serialized_data_sources = {
            name: df.to_dict("records") for name, df in self.data_sources.items()
        }
        self._excluded_kwargs: Set[str] = set(excluded_kwargs or [])
        self.show_doc_link = show_doc_link
        self.multi_chart = multi_chart

        super().__init__(id=self.ids.container(component_id), children=self._build_layout(), **kwargs)

    def _build_layout(self):
        data_source_keys = list(self.data_sources.keys())
        default_data = data_source_keys[0] if data_source_keys else None
        chart_models = _get_chart_union_models()
        default_chart_model = chart_models[0]

        initial_state = _EditorState(
            charts=[
                default_chart_model(
                    label="Chart 1",
                    data_source=default_data,
                )
            ],
            shared_layout=_LayoutConfig(),
        )

        return [
            dmc.MantineProvider(
                html.Div(
                    [
                        html.H4("Chart Editor", style={"marginBottom": "20px"}),
                        ModelForm(
                            item=initial_state,
                            aio_id=self.component_id,
                            form_id=self._FORM_ID,
                            form_layout=AccordionFormLayout(
                                sections=[
                                    FormSection(
                                        name="Charts",
                                        fields=["charts"],
                                        default_open=True,
                                    ),
                                    FormSection(
                                        name="Layout",
                                        fields=["shared_layout"],
                                        description=(
                                            "Configure layout properties shared across all charts, "
                                            "such as title, legend position, and background colour."
                                        ),
                                    ),
                                ]
                            ),
                        ),
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
                            "editable": True,        # allow in-chart title / axis / annotation editing
                            "displayModeBar": True,
                        },
                    ),
                    html.Pre(
                        id=self.ids.debug(self.component_id),
                        style={"whiteSpace": "pre-wrap", "fontSize": "12px", "color": "#666"},
                    ),
                    dcc.Store(id=self.ids.data_sources(self.component_id), data=self._serialized_data_sources),
                ],
                style={"width": "63%", "display": "inline-block", "marginLeft": "2%"},
            ),
        ]

    # ── Utility methods ────────────────────────────────────────────────────────

    @staticmethod
    def _to_figure(chart_type: str, data_frame: pd.DataFrame, chart_kwargs: dict) -> go.Figure:
        """Call the Plotly Express function for chart_type, filtering out blank kwargs."""
        chart_fn = getattr(px, chart_type)
        clean_kwargs = {
            k: v for k, v in chart_kwargs.items()
            if v is not None and v != "" and v != []
        }
        return chart_fn(data_frame=data_frame, **clean_kwargs)

    @staticmethod
    def _build_form_model(chart_type: str, columns: List[str], excluded: Set[str]) -> type[BaseModel]:
        """Build a dynamic pydantic model for a chart type's kwargs.

        Kept as a utility method for advanced / programmatic use.  The main editor
        now uses the static ``_ChartEntry`` model rendered via ``_EditorState``.
        """
        metadata = PX_CHART_METADATA[chart_type]
        column_kwargs = set(metadata["column_kwargs"])
        multi_column_kwargs = set(metadata["multi_column_kwargs"])
        fixed_options: dict = metadata.get("fixed_options", {})
        param_defaults: dict = metadata.get("param_defaults", {})
        param_descriptions: dict = metadata.get("param_descriptions", {})

        fields: dict = {}
        literal_columns = tuple(columns)

        for arg in metadata["kwargs"]:
            if arg in excluded:
                continue

            title = arg.replace("_", " ").title()
            sig_default = param_defaults.get(arg)
            desc = param_descriptions.get(arg, "")

            if arg in multi_column_kwargs:
                if literal_columns:
                    field_type = Optional[List[Literal[literal_columns]]]  # type: ignore[valid-type]
                else:
                    field_type = Optional[List[str]]
                fields[arg] = (field_type, Field(default=None, title=title, description=desc or None))
                continue

            if arg in column_kwargs:
                if literal_columns:
                    field_type = Optional[Literal[literal_columns]]  # type: ignore[valid-type]
                else:
                    field_type = Optional[str]
                fields[arg] = (field_type, Field(default=None, title=title, description=desc or None))
                continue

            if arg in fixed_options:
                opts = tuple(dict.fromkeys(fixed_options[arg]))
                if opts:
                    field_type = Optional[Literal[opts]]  # type: ignore[valid-type]
                    field_default = sig_default if isinstance(sig_default, str) and sig_default in opts else None
                    fields[arg] = (field_type, Field(default=field_default, title=title, description=desc or None))
                    continue

            if arg in NUMERIC_CONSTRAINTS:
                nc = NUMERIC_CONSTRAINTS[arg]
                num_type = nc["type"]
                field_kwargs: dict = {"title": title}
                if desc:
                    field_kwargs["description"] = desc
                if "ge" in nc:
                    field_kwargs["ge"] = nc["ge"]
                if "le" in nc:
                    field_kwargs["le"] = nc["le"]
                if "multiple_of" in nc:
                    field_kwargs["multiple_of"] = nc["multiple_of"]
                num_default = sig_default if isinstance(sig_default, (int, float)) and not isinstance(sig_default, bool) else None
                fields[arg] = (Optional[num_type], Field(default=num_default, **field_kwargs))
                continue

            inferred = metadata["arg_types"].get(arg, str)
            if inferred in (bool, int, float, dict, list, str):
                field_type = Optional[inferred]
            else:
                field_type = Optional[str]
            fields[arg] = (field_type, Field(default=None, title=title, description=desc or None))

        return create_model(f"{chart_type.title()}Form", **fields)

    # ── Column fields read from each _ChartEntry ───────────────────────────────
    _COLUMN_FIELDS = ("x", "y", "color", "size", "names", "values")

    @staticmethod
    def _entry_to_figure(entry: _ChartEntry, all_sources: dict) -> Optional[go.Figure]:
        """Render a single _ChartEntry as a Plotly figure, or return None if not renderable."""
        if not entry.chart_type or not entry.data_source:
            return None
        records = all_sources.get(entry.data_source, [])
        if not records:
            return None
        df = pd.DataFrame(records)

        kwargs: dict = {}
        for field_name in (*PydanticChartEditor._COLUMN_FIELDS, "opacity"):
            val = getattr(entry, field_name, None)
            if val is not None and val != "":
                kwargs[field_name] = val

        # Need at least one column kwarg to render a meaningful chart
        if not any(kwargs.get(f) for f in PydanticChartEditor._COLUMN_FIELDS):
            return None

        return PydanticChartEditor._to_figure(entry.chart_type, df, kwargs)

    @staticmethod
    def _apply_shared_layout(fig: go.Figure, layout_cfg: _LayoutConfig) -> None:
        """Apply shared _LayoutConfig settings to the figure in-place."""
        layout_dict = layout_cfg.model_dump(exclude_none=True)
        legend_update: dict = {}
        layout_update: dict = {}
        for key, val in layout_dict.items():
            if val is None or val == "" or val == []:
                continue
            if key.startswith("legend_"):
                legend_update[key[len("legend_"):]] = val
            else:
                layout_update[key] = val
        if legend_update:
            layout_update["legend"] = legend_update
        if layout_update:
            fig.update_layout(**layout_update)

    # ── Auto-wired AIO callbacks ───────────────────────────────────────────────

    @staticmethod
    @callback(
        Output(ids.chart(MATCH), "figure"),
        Output(ids.debug(MATCH), "children"),
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        State(ids.data_sources(MATCH), "data"),
        State(ids.chart(MATCH), "relayoutData"),
    )
    def render_combined_figure(form_data, serialized_data_sources, relayout_data):
        """Render all charts in the list as traces on a shared dcc.Graph.

        Reads the unified ``_EditorState`` from the ModelForm data store, renders
        each chart entry as a Plotly Express figure, combines all traces, then
        applies the shared layout and any in-graph user edits from relayoutData.
        """
        if not form_data:
            return go.Figure(), ""

        try:
            state = _EditorState.model_validate(form_data)
        except ValidationError as exc:
            err_fig = go.Figure()
            err_fig.update_layout(title=f"State validation error: {exc}")
            return err_fig, str(exc)

        all_sources = serialized_data_sources or {}
        fig = go.Figure()
        has_data = False
        render_errors: list = []

        for chart_entry in state.charts:
            try:
                trace_fig = PydanticChartEditor._entry_to_figure(chart_entry, all_sources)
            except Exception as exc:  # pragma: no cover – surfaced in debug output below
                render_errors.append(f"Error rendering '{chart_entry.label}': {exc}")
                continue
            if trace_fig is None:
                continue
            for trace in trace_fig.data:
                trace.name = chart_entry.label or chart_entry.chart_type or "Chart"
                fig.add_trace(trace)
            has_data = True

        if not has_data:
            debug = "\n".join(render_errors) if render_errors else "Select chart type, data source, and at least one column to render."
            return go.Figure(), debug

        PydanticChartEditor._apply_shared_layout(fig, state.shared_layout)

        # Re-apply any in-graph user edits that are not captured by the layout form.
        if relayout_data:
            _apply_relayout(fig, relayout_data)

        debug = json.dumps(form_data, indent=2, default=str)
        if render_errors:
            debug = "\n".join(render_errors) + "\n\n" + debug
        return fig, debug

    @staticmethod
    @callback(
        Output(ModelForm.ids.form(MATCH, _PYDF_FORM_ID), "data-update"),
        Input(ids.chart(MATCH), "relayoutData"),
        State(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        prevent_initial_call=True,
    )
    def sync_relayout_to_form(relayout_data, current_data):
        """Sync in-graph edits (title, legend, bgcolor, …) back to the layout form section.

        When the user edits a chart element directly (e.g. clicks the title, drags the
        legend), Plotly fires ``relayoutData``.  This callback maps the changed keys to the
        corresponding ``_LayoutConfig`` fields via ``_RELAYOUT_TO_LAYOUT`` and writes them
        back into the ModelForm store so the form and the chart stay in step.
        """
        if not relayout_data:
            return no_update

        current = dict(current_data or {})
        layout = dict(current.get("shared_layout") or {})
        changed = False
        for relayout_key, layout_field in _RELAYOUT_TO_LAYOUT.items():
            if relayout_key in relayout_data:
                layout[layout_field] = relayout_data[relayout_key]
                changed = True

        if changed:
            current["shared_layout"] = layout
            return current
        return no_update


def create_pydantic_chart_editor_app(
    data_sources: Dict[str, pd.DataFrame],
    port: int = 8054,
    excluded_kwargs: Optional[Set[str]] = None,
    show_doc_link: bool = True,
    multi_chart: bool = True,
):
    app = dash.Dash(__name__)
    editor = PydanticChartEditor(
        data_sources=data_sources,
        component_id="main-editor",
        excluded_kwargs=excluded_kwargs,
        show_doc_link=show_doc_link,
        multi_chart=multi_chart,
    )

    app.layout = html.Div([
        html.H1("Pydantic Chart Editor", style={"textAlign": "center", "marginBottom": "20px"}),
        editor,
    ])

    return app


def get_chart_union_models() -> List[type[BaseModel]]:
    """Public helper exposing dynamically created per-chart models."""
    return _get_chart_union_models()
