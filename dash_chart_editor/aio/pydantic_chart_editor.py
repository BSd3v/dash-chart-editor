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

from .px_metadata import PX_CHART_METADATA, NUMERIC_CONSTRAINTS, classify_chart_param

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




_DYNAMIC_CHART_MODELS: Optional[List[type[BaseModel]]] = None
_DYNAMIC_CHART_UNION: Optional[Any] = None
_DYNAMIC_EDITOR_STATE_MODEL: Optional[type[BaseModel]] = None


def _build_chart_param_field(arg: str, metadata: dict) -> tuple:
    """Return a (type, Field) pair for a single chart parameter."""
    fixed_options: dict = metadata.get("fixed_options", {})
    param_defaults: dict = metadata.get("param_defaults", {})
    param_descriptions: dict = metadata.get("param_descriptions", {})
    column_kwargs = set(metadata.get("column_kwargs", []))
    multi_column_kwargs = set(metadata.get("multi_column_kwargs", []))

    title = arg.replace("_", " ").title()
    desc = param_descriptions.get(arg, "")
    sig_default = param_defaults.get(arg)

    if arg in multi_column_kwargs:
        return (Optional[List[str]], Field(default=None, title=title, description=desc or None))

    if arg in column_kwargs:
        return (Optional[str], Field(default=None, title=title, description=desc or None))

    if arg in fixed_options:
        opts = tuple(dict.fromkeys(fixed_options[arg]))
        if opts:
            field_type = Optional[Literal[opts]]  # type: ignore[valid-type]
            field_default = sig_default if isinstance(sig_default, str) and sig_default in opts else None
            return (field_type, Field(default=field_default, title=title, description=desc or None))

    if arg in NUMERIC_CONSTRAINTS:
        nc = NUMERIC_CONSTRAINTS[arg]
        fkw: dict = {"title": title}
        if desc:
            fkw["description"] = desc
        if "ge" in nc:
            fkw["ge"] = nc["ge"]
        if "le" in nc:
            fkw["le"] = nc["le"]
        if "multiple_of" in nc:
            fkw["multiple_of"] = nc["multiple_of"]
        num_default = (
            sig_default
            if isinstance(sig_default, (int, float)) and not isinstance(sig_default, bool)
            else None
        )
        return (Optional[nc["type"]], Field(default=num_default, **fkw))

    inferred = metadata.get("arg_types", {}).get(arg, str)
    if inferred in (bool, int, float, dict, list, str):
        field_type = Optional[inferred]
    else:
        field_type = Optional[str]
    return (field_type, Field(default=None, title=title, description=desc or None))


def _build_section_model(
    chart_type: str,
    section_name: str,
    params: List[str],
    metadata: dict,
) -> type[BaseModel]:
    """Build a pydantic model for one section (common/advanced/special) of a chart type."""
    fields: Dict[str, Any] = {
        arg: _build_chart_param_field(arg, metadata)
        for arg in params
    }
    return create_model(f"{chart_type.title()}{section_name.title()}Section", **fields)


def _build_dynamic_chart_options_model(chart_type: str, metadata: dict) -> type[BaseModel]:
    """Build a chart-entry model for a specific Plotly Express chart type.

    The model has three nested section sub-models:
    - **common** – core column selectors and opacity.
    - **advanced** – facets, animation, error bars, color scales, etc.
    - **special** – chart-type-specific params (trendlines, marginals, display modes, …).

    A ``model_validator(mode='before')`` accepts flat dicts (backward-compatible input)
    and reshapes them into the three sections automatically.
    """
    from pydantic import model_validator

    kwargs = metadata.get("kwargs", [])
    # Partition kwargs into sections, preserving original order within each.
    common_params = [p for p in kwargs if classify_chart_param(p) == "common"]
    advanced_params = [p for p in kwargs if classify_chart_param(p) == "advanced"]
    special_params = [p for p in kwargs if classify_chart_param(p) == "special"]

    CommonSection = _build_section_model(chart_type, "common", common_params, metadata)
    AdvancedSection = _build_section_model(chart_type, "advanced", advanced_params, metadata)
    SpecialSection = _build_section_model(chart_type, "special", special_params, metadata)

    # All kwarg names per section – used by the flat-input validator.
    _common_set = set(common_params)
    _advanced_set = set(advanced_params)
    _special_set = set(special_params)

    @model_validator(mode="before")
    @classmethod
    def _reshape_flat_input(cls, data: Any) -> Any:  # noqa: N805
        """Accept legacy flat dicts and fold them into section sub-dicts."""
        if not isinstance(data, dict):
            return data
        # If any section key already present, assume structured input.
        if any(k in data for k in ("common", "advanced", "special")):
            return data
        top: Dict[str, Any] = {}
        common_d: Dict[str, Any] = {}
        adv_d: Dict[str, Any] = {}
        spec_d: Dict[str, Any] = {}
        for k, v in data.items():
            if k in ("chart_type", "label", "data_source"):
                top[k] = v
            elif k in _common_set:
                common_d[k] = v
            elif k in _special_set:
                spec_d[k] = v
            elif k in _advanced_set:
                adv_d[k] = v
            # unknown keys dropped silently
        if common_d:
            top["common"] = common_d
        if adv_d:
            top["advanced"] = adv_d
        if spec_d:
            top["special"] = spec_d
        return top

    fields: Dict[str, Any] = {
        # chart_type is the Pydantic v2 discriminator field for the union.
        "chart_type": (Literal[chart_type], Field(default=chart_type, title="Chart Type")),
        "label": (str, Field(default="Chart", title="Label")),
        "data_source": (Optional[str], Field(default=None, title="Data Source")),
        "common": (
            CommonSection,
            Field(
                default_factory=CommonSection,
                title="Common",
                json_schema_extra={"default_open": True},
            ),
        ),
        "advanced": (
            AdvancedSection,
            Field(
                default_factory=AdvancedSection,
                title="Advanced",
                json_schema_extra={"default_open": False},
            ),
        ),
        "special": (
            SpecialSection,
            Field(
                default_factory=SpecialSection,
                title="Special",
                json_schema_extra={"default_open": False},
            ),
        ),
    }

    return create_model(
        f"{chart_type.title()}ChartEntry",
        __validators__={"_reshape_flat_input": _reshape_flat_input},
        **fields,
    )


def _get_chart_union_models() -> List[type[BaseModel]]:
    """Return list of per-chart models built from currently available px chart metadata."""
    global _DYNAMIC_CHART_MODELS
    if _DYNAMIC_CHART_MODELS is None:
        _DYNAMIC_CHART_MODELS = [
                _build_dynamic_chart_options_model(chart_type, PX_CHART_METADATA[chart_type])
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
    """Return dynamic editor-state model containing chart union list + shared layout.

    Each chart entry is a discriminated-union model (one per chart type) built at app
    startup from ``PX_CHART_METADATA``.  The union uses ``chart_type`` as the
    discriminator so pydantic selects the correct per-chart model automatically.
    Each per-chart model has three nested section sub-models (common / advanced / special)
    so pydf can render them in collapsible accordion panels.
    """
    global _DYNAMIC_EDITOR_STATE_MODEL
    if _DYNAMIC_EDITOR_STATE_MODEL is None:
        from typing import Annotated
        from pydantic import Field as PydField

        chart_union = _get_chart_union_type()
        AnnotatedUnion = Annotated[chart_union, PydField(discriminator="chart_type")]

        _DYNAMIC_EDITOR_STATE_MODEL = create_model(
            "_DynamicEditorState",
            charts=(
                List[AnnotatedUnion],  # type: ignore[valid-type]
                Field(
                    default_factory=list,
                    title="Charts",
                    description=(
                        "Configure individual chart traces. "
                        "Add multiple charts to overlay on the same graph."
                    ),
                ),
            ),
            shared_layout=(
                _LayoutConfig,
                Field(
                    default_factory=_LayoutConfig,
                    title="Layout",
                    description="Layout settings shared across all charts in this figure.",
                ),
            ),
        )
    return _DYNAMIC_EDITOR_STATE_MODEL


# Backward-compatible alias used in tests/imports.
_EditorState = _get_editor_state_model()

# Simple flat backward-compat model for external code / older tests that import _ChartEntry.
# NOTE: This is NOT used by the live ModelForm-based editor; the discriminated-union models
# generated by _build_dynamic_chart_options_model are used for the actual editor state.
_ChartEntry = create_model(
    "_ChartEntry",
    chart_type=(str, Field(default="scatter", title="Chart Type")),
    label=(str, Field(default="Chart", title="Label")),
    data_source=(Optional[str], Field(default=None, title="Data Source")),
    x=(Optional[str], Field(default=None, title="X")),
    y=(Optional[str], Field(default=None, title="Y")),
    color=(Optional[str], Field(default=None, title="Color")),
    size=(Optional[str], Field(default=None, title="Size")),
    names=(Optional[str], Field(default=None, title="Names")),
    values=(Optional[str], Field(default=None, title="Values")),
    opacity=(Optional[float], Field(default=None, title="Opacity", ge=0.0, le=1.0)),
)



class PydanticChartEditor(html.Div):
    """Standalone chart editor using dash-pydantic-form.

        The editor renders a ``ModelForm`` for ``_EditorState``, which contains:
        - **Charts** accordion section — a pydantic-form list of dynamic chart entry items,
            each with chart type, data source, and chart-type-specific options. The list supports
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
        chart_union_models = _get_chart_union_models()
        default_chart_model = chart_union_models[0] if chart_union_models else None
        default_entry = default_chart_model(label="Chart 1", data_source=default_data) if default_chart_model else None

        initial_state = _EditorState(
            charts=[default_entry.model_dump()] if default_entry else [],
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

    # ── Column fields used to check if any column is selected ───────────────────────────────
    # Subset of COMMON_PARAM_NAMES that are actual column references (not opacity/hover_data/etc.)
    # used to decide whether a meaningful chart can be rendered.
    _COLUMN_FIELDS = ("x", "y", "z", "r", "theta", "color", "size", "names", "values",
                      "lat", "lon", "locations", "hover_name")

    # Fields to skip when flattening section sub-models into Plotly Express kwargs.
    _SECTION_SKIP: frozenset = frozenset({"label", "chart_type", "data_source",
                                          "common", "advanced", "special"})

    @staticmethod
    def _flatten_entry_kwargs(entry) -> dict:
        """Flatten kwargs from an entry's section sub-models (common, advanced, special).

        Each per-chart-type entry model has three nested section sub-models.  This helper
        collects all non-None values from each section into a single flat dict ready to
        pass to Plotly Express.  It also handles flat entries (backward-compat ``_ChartEntry``
        instances that expose kwargs directly as top-level attributes).
        """
        kwargs: dict = {}
        # Try section sub-models first (new section-based architecture).
        for section_name in ("common", "advanced", "special"):
            section = getattr(entry, section_name, None)
            if section is not None and hasattr(section, "model_dump"):
                for k, v in section.model_dump(exclude_none=True).items():
                    if v is not None and v != "" and v != []:
                        kwargs[k] = v
        if not kwargs:
            # Fall back to reading flat top-level fields (backward-compat flat models).
            for k, v in entry.model_dump(exclude_none=True).items():
                if k not in PydanticChartEditor._SECTION_SKIP and v is not None and v != "" and v != []:
                    kwargs[k] = v
        return kwargs

    @staticmethod
    def _entry_to_figure(entry, all_sources: dict) -> Optional[go.Figure]:
        """Render a single chart entry as a Plotly figure, or return None if not renderable."""
        data_source = getattr(entry, "data_source", None)
        if not data_source:
            return None
        records = all_sources.get(data_source, [])
        if not records:
            return None
        df = pd.DataFrame(records)

        kwargs = PydanticChartEditor._flatten_entry_kwargs(entry)

        # Need at least one column kwarg to render a meaningful chart.
        if not any(kwargs.get(f) for f in PydanticChartEditor._COLUMN_FIELDS):
            return None

        chart_type = getattr(entry, "chart_type", None)
        return PydanticChartEditor._to_figure(chart_type, df, kwargs)

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
                label = getattr(chart_entry, "label", None)
                chart_type = getattr(chart_entry, "chart_type", None)
                render_errors.append(f"Error rendering '{label or chart_type}': {exc}")
                continue
            if trace_fig is None:
                continue
            for trace in trace_fig.data:
                label = getattr(chart_entry, "label", None)
                chart_type = getattr(chart_entry, "chart_type", None)
                trace.name = label or chart_type or "Chart"
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
