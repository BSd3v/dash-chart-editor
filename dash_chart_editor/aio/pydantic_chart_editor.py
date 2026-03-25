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
from dash_pydantic_form import fields as pydf_fields

from .px_metadata import (
    PX_CHART_METADATA, NUMERIC_CONSTRAINTS, classify_chart_param,
    COMMON_PARAM_NAMES,
)
from pydantic import model_validator

_PYDF_FORM_ID = "pydantic-chart-editor-form"

# All chart type names available from Plotly Express metadata.
_CHART_TYPES: tuple = tuple(sorted(PX_CHART_METADATA.keys()))

# All single-column and multi-column kwargs across all chart types (for column value cleaning).
_ALL_SINGLE_COL_KWARGS: frozenset = frozenset(
    kw for meta in PX_CHART_METADATA.values() for kw in meta.get("column_kwargs", [])
)
_ALL_MULTI_COL_KWARGS: frozenset = frozenset(
    kw for meta in PX_CHART_METADATA.values() for kw in meta.get("multi_column_kwargs", [])
# x and y appear in multi_column_kwargs for some chart types but are handled as single-column
# Select fields; exclude them here so they are cleaned via _ALL_SINGLE_COL_KWARGS instead.
) - frozenset({"x", "y"})

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
FORM_PANEL_MAX_HEIGHT = "85vh"


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


# ── Data transform models ─────────────────────────────────────────────────────

# Pandas aggregation functions exposed in the UI.
_AGG_FUNCTIONS = Literal[  # type: ignore[assignment]
    "sum", "mean", "median", "min", "max", "count", "std", "var", "first", "last"
]

# Pandas sort directions
_SORT_DIRECTIONS = Literal["asc", "desc"]  # type: ignore[assignment]


class _DataFilter(BaseModel):
    """A single column filter applied to the DataFrame before charting."""

    column: Optional[str] = Field(default=None, title="Column",
                                   description="DataFrame column to filter on.")
    operator: Optional[Literal["==", "!=", ">", ">=", "<", "<="]] = Field(
        default="==", title="Operator",
        description="Comparison operator used for the filter.")
    value: Optional[str] = Field(default=None, title="Value",
                                  description="Value to compare against (strings are auto-cast).")


class _DataGroupBy(BaseModel):
    """Group-by + aggregation applied to the DataFrame before charting."""

    group_by_columns: List[str] = Field(
        default_factory=list,
        title="Group By Columns",
        description="One or more columns to group by.",
    )
    agg_columns: List[str] = Field(
        default_factory=list,
        title="Aggregate Columns",
        description="One or more columns to aggregate. Leave empty to count rows per group.",
    )
    agg_function: Optional[_AGG_FUNCTIONS] = Field(  # type: ignore[assignment]
        default="sum", title="Aggregation Function",
        description="Aggregation applied to the selected column.")

    @staticmethod
    def _normalize_to_str_list(v: Any) -> List[str]:
        """Normalize a single string or list of strings to a clean list."""
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [v]
        # Only string column names are supported for group and aggregate fields.
        if isinstance(v, list):
            # Keep only non-empty string tokens so tag-style list inputs stay clean.
            return [item for item in v if isinstance(item, str) and item]
        return []

    @model_validator(mode="before")
    @classmethod
    def _normalize_groupby_fields(cls, value: Any) -> Any:
        """Normalize legacy singular keys and string inputs into list fields."""
        if not isinstance(value, dict):
            return value

        result = dict(value)

        # Backward compatibility for legacy payloads.
        if "group_by" in result and "group_by_columns" not in result:
            result["group_by_columns"] = result.get("group_by")
        if "agg_column" in result and "agg_columns" not in result:
            result["agg_columns"] = result.get("agg_column")
        # Remove legacy keys after migration.
        result.pop("group_by", None)
        result.pop("agg_column", None)

        result["group_by_columns"] = cls._normalize_to_str_list(result.get("group_by_columns"))
        result["agg_columns"] = cls._normalize_to_str_list(result.get("agg_columns"))
        return result


class _DataSort(BaseModel):
    """Sort order applied to the DataFrame before charting."""

    sort_by: Optional[str] = Field(default=None, title="Sort By Column",
                                    description="Column to sort by.")
    direction: Optional[_SORT_DIRECTIONS] = Field(  # type: ignore[assignment]
        default="asc", title="Direction",
        description="Sort direction: 'asc' (ascending) or 'desc' (descending).")


class _DataTransforms(BaseModel):
    """Per-chart data transforms applied to the DataFrame before it is passed to Plotly."""

    filters: List[_DataFilter] = Field(
        default_factory=list,
        title="Filters",
        description=(
            "Row filters applied in sequence. "
            "Add one entry per column you want to filter on."
        ),
    )
    group_by: Optional[_DataGroupBy] = Field(
        default_factory=_DataGroupBy,
        title="Group By",
        description="Optionally group and aggregate the data before charting.",
    )
    sort: Optional[_DataSort] = Field(
        default_factory=_DataSort,
        title="Sort",
        description="Optionally sort rows before charting.",
    )


def _apply_transforms(df: pd.DataFrame, transforms: Optional[_DataTransforms]) -> pd.DataFrame:
    """Apply data transforms (filters, group-by, sort) to *df* and return the result.

    Each step is skipped gracefully when its required fields are not set, so the
    chart still renders even if a transform is only partially configured.
    """
    if transforms is None:
        return df

    # 1. Filters – applied in the order they are declared.
    for f in (transforms.filters or []):
        col = f.column
        op = f.operator or "=="
        val_raw = f.value
        if not col or col not in df.columns or val_raw is None or val_raw == "":
            continue
        # Auto-cast value to the column dtype where possible.
        try:
            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                val: Any = float(val_raw)
                if pd.api.types.is_integer_dtype(series):
                    val = int(val)
            elif pd.api.types.is_bool_dtype(series):
                val = val_raw.lower() in ("true", "1", "yes")
            else:
                val = val_raw
        except (ValueError, TypeError):
            val = val_raw
        try:
            mask = {
                "==": series == val,
                "!=": series != val,
                ">":  series > val,
                ">=": series >= val,
                "<":  series < val,
                "<=": series <= val,
            }[op]
            df = df[mask]
        except (TypeError, KeyError):
            pass  # Skip invalid comparison rather than crash.

    # 2. Group-by / aggregation.
    gb = transforms.group_by
    group_cols = [col for col in (gb.group_by_columns if gb else []) if col in df.columns]
    if gb and group_cols:
        agg_fn = gb.agg_function or "sum"
        agg_cols = [col for col in gb.agg_columns if col in df.columns]
        if agg_cols:
            df = df.groupby(group_cols, as_index=False)[agg_cols].agg(agg_fn)
        else:
            # Count rows per group.
            df = df.groupby(group_cols, as_index=False).size().rename(columns={"size": "count"})

    # 3. Sort.
    s = transforms.sort
    if s and s.sort_by and s.sort_by in df.columns:
        df = df.sort_values(s.sort_by, ascending=(s.direction != "desc"))

    return df


# ─────────────────────────────────────────────────────────────────────────────

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
            if k in ("chart_type", "name", "data_source"):
                top[k] = v
            elif k == "label":
                # Backward compatibility: legacy payloads used "label".
                top["name"] = v
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
        "name": (str, Field(default="Chart", title="Name")),
        "data_source": (Optional[str], Field(default=None, title="Data Source")),
        "common": (
            CommonSection,
            Field(
                default_factory=CommonSection,
                title="Common",
            ),
        ),
        "advanced": (
            AdvancedSection,
            Field(
                default_factory=AdvancedSection,
                title="Advanced",
            ),
        ),
        "special": (
            SpecialSection,
            Field(
                default_factory=SpecialSection,
                title="Special",
            ),
        ),
        "transforms": (
            _DataTransforms,
            Field(
                default_factory=_DataTransforms,
                title="Transforms",
                description=(
                    "Optional data transforms applied before the chart is rendered. "
                    "Add filters to narrow rows, group-by to aggregate, or sort to order data."
                ),
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
    name=(str, Field(default="Chart", title="Name")),
    data_source=(Optional[str], Field(default=None, title="Data Source")),
    x=(Optional[str], Field(default=None, title="X")),
    y=(Optional[str], Field(default=None, title="Y")),
    color=(Optional[str], Field(default=None, title="Color")),
    size=(Optional[str], Field(default=None, title="Size")),
    names=(Optional[str], Field(default=None, title="Names")),
    values=(Optional[str], Field(default=None, title="Values")),
    opacity=(Optional[float], Field(default=None, title="Opacity", ge=0.0, le=1.0)),
)


from dash_pydantic_form.form_layouts.form_layout import FormLayout
from typing import Any, Literal
from dash import html


def _build_charts_fields_repr(
    data_source_names: list,
    all_columns: list,
) -> dict:
    """Build the ``fields_repr`` dict for the ``charts`` list in ModelForm.

    Overrides:
    - ``data_source`` → Select dropdown populated with *data_source_names*.
    - All column kwargs (x, y, color, etc.) in every section → Select or MultiSelect
      dropdowns populated with *all_columns* (union of columns across all data sources).
    - Transform column fields (filter column, group-by columns, sort column) → same.

    Returns a dict suitable for ``ModelForm(fields_repr={"charts": ...})``.
    The returned dict always contains ``"form_layout"``.  ``"fields_repr"`` is only
    added when there are data source names or columns to populate — an empty override
    dict would be ignored by pydf but is omitted here for clarity.
    """
    charts_repr: dict = {"form_layout": FlatSectionFormLayout()}
    inner: dict = {}

    if data_source_names:
        ds_labels = {name: name for name in data_source_names}
        inner["data_source"] = pydf_fields.Select(options_labels=ds_labels)

    if all_columns:
        col_labels = {col: col for col in all_columns}

        # Collect ALL column kwargs across all chart types, split into single/multi.
        single_col_kwargs: set = set()
        multi_col_kwargs: set = set()
        for ct_meta in PX_CHART_METADATA.values():
            single_col_kwargs.update(ct_meta.get("column_kwargs", []))
            multi_col_kwargs.update(ct_meta.get("multi_column_kwargs", []))
        # x and y are forced to single-column (see px_metadata convention).
        multi_col_kwargs -= {"x", "y"}

        def _build_section_col_repr(section_name: str) -> dict:
            """Return {field_name: Select/MultiSelect} for column fields in this section."""
            rep: dict = {}
            for f in single_col_kwargs:
                if classify_chart_param(f) == section_name:
                    rep[f] = pydf_fields.Select(options_labels=col_labels)
            for f in multi_col_kwargs:
                if classify_chart_param(f) == section_name:
                    rep[f] = pydf_fields.MultiSelect(options_labels=col_labels)
            return rep

        for section in ("common", "advanced", "special"):
            section_repr = _build_section_col_repr(section)
            if section_repr:
                inner[section] = {"fields_repr": section_repr}

        # Transforms: column fields for filters, group-by, sort.
        inner["transforms"] = {
            "fields_repr": {
                "filters": {
                    "fields_repr": {
                        "column": pydf_fields.Select(options_labels=col_labels),
                    }
                },
                "group_by": {
                    "fields_repr": {
                        "group_by_columns": pydf_fields.MultiSelect(options_labels=col_labels),
                        "agg_columns": pydf_fields.MultiSelect(options_labels=col_labels),
                    }
                },
                "sort": {
                    "fields_repr": {
                        "sort_column": pydf_fields.Select(options_labels=col_labels),
                    }
                },
            }
        }

    if inner:
        charts_repr["fields_repr"] = inner

    return charts_repr


class FlatSectionFormLayout(FormLayout):
    layout: Literal["flat-section"] = "flat-section"
    color: str = "red"

    def render(
        self,
        *,
        field_inputs: dict[str, Any],
        aio_id: str,
        form_id: str,
        path: str,
        read_only: bool,
        form_cols: int,
    ) -> list:
        def extract_fields(component):
            # If this is a list, flatten all children
            if isinstance(component, list):
                result = []
                for c in component:
                    result.extend(extract_fields(c))
                return result
            # If this is an AccordionItem, stop here
            if isinstance(component, dmc.AccordionItem):
                return component
            # If this is a Dash component with children, recurse
            if hasattr(component, "children"):
                return extract_fields(component.children)
            # Otherwise, this is a leaf node (input field)
            return None
        
        # Helper to flatten a subform's fields
        def flatten_subform(subform, value=None):
            # return first accordion item children if it's an AccordionFormLayout, otherwise assume it's already flat
            new_item = extract_fields(subform)
            if new_item and isinstance(new_item, dmc.AccordionItem):
                new_item.value = value
            return new_item
        
        # Get subforms for each section
        common_subform = field_inputs.get("common")
        advanced_subform = field_inputs.get("advanced")
        special_subform = field_inputs.get("special")
        transorms_subform = field_inputs.get("transforms")

        return [
            html.Div([
                field_inputs.get("chart_type", html.Div("No chart_type field found")),
                field_inputs.get("name"),
                field_inputs.get("data_source"),
                dmc.Accordion(children=[
                    (flatten_subform(common_subform, 'common') if common_subform else None),
                    (flatten_subform(advanced_subform, 'advanced') if advanced_subform else None),
                    (flatten_subform(special_subform, 'special') if special_subform else None),
                    (flatten_subform(transorms_subform, 'transforms') if transorms_subform else None),
                ],
                value='common',
                multiple=False,
                style={"marginTop": "15px"})
            ])
        ]

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

        @staticmethod
        def form_wrapper(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "form-wrapper", "aio_id": aio_id}

        @staticmethod
        def selected_sources_store(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "selected-sources", "aio_id": aio_id}

        @staticmethod
        def col_names_store(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "col-names", "aio_id": aio_id}

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
        default_entry = default_chart_model(name="Chart 1", data_source=default_data) if default_chart_model else None

        initial_state = _EditorState(
            charts=[default_entry.model_dump()] if default_entry else [],
            shared_layout=_LayoutConfig(),
        )

        # Union of all columns from all data sources — used to populate column Select dropdowns.
        all_columns: list = sorted(
            set(col for df in self.data_sources.values() for col in df.columns)
        )
        charts_fields_repr = _build_charts_fields_repr(data_source_keys, all_columns)

        return html.Div(
            [
                dmc.MantineProvider(
                    html.Div(
                        [
                            html.H4("Chart Editor", style={"marginBottom": "20px"}),
                            html.Div(
                                id=self.ids.form_wrapper(self.component_id),
                                children=[
                                    PydanticChartEditor._build_model_form(
                                        self.component_id,
                                        self._FORM_ID,
                                        initial_state,
                                        charts_fields_repr,
                                    )
                                ],
                            ),
                        ],
                        style={
                            "width": "35%",
                            "padding": "20px",
                            "maxHeight": FORM_PANEL_MAX_HEIGHT,
                            "overflowY": "auto",
                            "position": "sticky",
                            "top": "10px",
                        },
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
                        dcc.Store(id=self.ids.selected_sources_store(self.component_id), data=[]),
                        dcc.Store(
                            id=self.ids.col_names_store(self.component_id),
                            data={name: list(df.columns) for name, df in self.data_sources.items()},
                        ),
                    ],
                    style={"width": "63%"},
                ),
            ],
            style={
                "display": "flex",
                "gap": "2%",
                "alignItems": "flex-start",
            },
        )

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
    # Keep legacy 'label' here so old payloads never leak it into Plotly Express calls
    # as an unexpected kwarg during flattening.
    _SECTION_SKIP: frozenset = frozenset({"name", "label", "chart_type", "data_source",
                                          "common", "advanced", "special", "transforms"})

    # Transform sub-fields that are column references (need cleaning when data source changes)
    _TRANSFORM_COL_FIELDS: frozenset = frozenset({"column", "sort_column"})
    _TRANSFORM_MULTI_COL_FIELDS: frozenset = frozenset({"group_by_columns", "agg_columns"})

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
    def _entry_display_name(entry) -> Optional[str]:
        """Return the best available display name for a chart entry."""
        return getattr(entry, "name", None) or getattr(entry, "label", None)

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

        # Apply per-entry data transforms (filters, group-by, sort) before charting.
        transforms = getattr(entry, "transforms", None)
        if transforms is not None:
            try:
                df = _apply_transforms(df, transforms)
            except (ValueError, TypeError, KeyError, AttributeError):
                pass  # Skip malformed transform config rather than crash the chart.

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

    @staticmethod
    def _clean_form_data_for_sources(form_data: dict, col_names: dict) -> dict:
        """Clear column field values that don't belong to the entry's selected data source.

        ``col_names`` maps source_name → [column, ...].
        Returns a new form_data dict with invalid column values removed.
        """
        if not form_data:
            return form_data
        result = dict(form_data)
        charts = list(result.get("charts", []))
        new_charts = []
        for chart in charts:
            if not isinstance(chart, dict):
                new_charts.append(chart)
                continue
            chart = dict(chart)
            ds = chart.get("data_source")
            valid_cols: set = set(col_names.get(ds, [])) if ds and col_names else set()
            if not valid_cols:
                new_charts.append(chart)
                continue
            # Clean section sub-model column fields
            for section_name in ("common", "advanced", "special"):
                section = chart.get(section_name)
                if not isinstance(section, dict):
                    continue
                cleaned: dict = {}
                for k, v in section.items():
                    if k in _ALL_SINGLE_COL_KWARGS:
                        if isinstance(v, str) and v in valid_cols:
                            cleaned[k] = v
                        # else: drop invalid column
                    elif k in _ALL_MULTI_COL_KWARGS:
                        if isinstance(v, list):
                            kept = [c for c in v if c in valid_cols]
                            if kept:
                                cleaned[k] = kept
                    else:
                        cleaned[k] = v
                chart[section_name] = cleaned
            # Clean transform column fields
            transforms = chart.get("transforms")
            if isinstance(transforms, dict):
                transforms = dict(transforms)
                filters = transforms.get("filters", [])
                if isinstance(filters, list):
                    transforms["filters"] = [
                        # Preserve non-dict entries as-is (e.g., already-serialized filter objects)
                        f for f in filters if not isinstance(f, dict) or f.get("column") in valid_cols
                    ]
                gb = transforms.get("group_by")
                if isinstance(gb, dict):
                    gb = dict(gb)
                    if "group_by_columns" in gb:
                        gb["group_by_columns"] = [c for c in (gb["group_by_columns"] or []) if c in valid_cols]
                    if "agg_columns" in gb:
                        gb["agg_columns"] = [c for c in (gb["agg_columns"] or []) if c in valid_cols]
                    transforms["group_by"] = gb
                sort = transforms.get("sort")
                if isinstance(sort, dict):
                    sort = dict(sort)
                    if sort.get("sort_column") not in valid_cols:
                        # Set to None (not deleted) so Pydantic validation clears the Optional field.
                        sort["sort_column"] = None
                    transforms["sort"] = sort
                chart["transforms"] = transforms
            new_charts.append(chart)
        result["charts"] = new_charts
        return result

    @staticmethod
    def _build_model_form(aio_id: str, form_id: str, state: "_EditorState", charts_fields_repr: dict) -> "ModelForm":
        """Build a ModelForm component for the given state and fields_repr."""
        return ModelForm(
            item=state,
            aio_id=aio_id,
            form_id=form_id,
            form_layout=AccordionFormLayout(
                sections=[
                    FormSection(name="Charts", fields=["charts"], default_open=True),
                    FormSection(
                        name="Layout",
                        fields=["shared_layout"],
                        description=(
                            "Configure layout properties shared across all charts, "
                            "such as title, legend position, and background color."
                        ),
                    ),
                ]
            ),
            fields_repr={"charts": charts_fields_repr},
        )

    # ── Auto-wired AIO callbacks ───────────────────────────────────────────────

    @staticmethod
    @callback(
        Output(ids.selected_sources_store(MATCH), "data"),
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        State(ids.selected_sources_store(MATCH), "data"),
        prevent_initial_call=True,
    )
    def track_selected_sources(form_data, prev_sources):
        """Track which data_source each chart entry has selected.

        Only updates the store when the list of selected sources actually changes,
        which breaks potential circular-update chains with rebuild_form_on_source_change.
        """
        if not form_data:
            return no_update
        charts = form_data.get("charts", [])
        new_sources = [
            c.get("data_source") if isinstance(c, dict) else None
            for c in charts
        ]
        if new_sources == (prev_sources or []):
            return no_update
        return new_sources

    @staticmethod
    @callback(
        Output(ids.form_wrapper(MATCH), "children"),
        Input(ids.selected_sources_store(MATCH), "data"),
        State(ids.col_names_store(MATCH), "data"),
        State(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data"),
        prevent_initial_call=True,
    )
    def rebuild_form_on_source_change(selected_sources, col_names, form_data):
        """Rebuild the ModelForm with column dropdowns filtered to currently selected sources.

        Computes the union of columns from all currently selected data sources across all
        chart entries, rebuilds ``fields_repr`` with those as dropdown options, clears any
        column values that are no longer valid for the newly selected source, then
        re-renders the ModelForm with the cleaned state and updated field options.
        """
        if not selected_sources or not col_names:
            return no_update

        from dash import callback_context
        triggered = callback_context.triggered_id
        aio_id = triggered.get("aio_id") if isinstance(triggered, dict) else None
        if not aio_id:
            return no_update

        # Columns from all currently-selected sources (union)
        selected_cols: set = set()
        for src in selected_sources:
            if src and src in col_names:
                selected_cols.update(col_names[src])
        all_selected_cols = sorted(selected_cols)

        # Rebuild fields_repr with filtered column options
        data_source_names = list(col_names.keys())
        charts_fields_repr = _build_charts_fields_repr(data_source_names, all_selected_cols)

        # Clean invalid column values from form data
        cleaned = PydanticChartEditor._clean_form_data_for_sources(form_data or {}, col_names)
        try:
            state = _EditorState.model_validate(cleaned)
        except Exception:
            try:
                state = _EditorState.model_validate(form_data or {})
            except Exception:
                return no_update

        form_id = PydanticChartEditor._FORM_ID
        return [PydanticChartEditor._build_model_form(aio_id, form_id, state, charts_fields_repr)]

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
                label = PydanticChartEditor._entry_display_name(chart_entry)
                chart_type = getattr(chart_entry, "chart_type", None)
                render_errors.append(f"Error rendering '{label or chart_type}': {exc}")
                continue
            if trace_fig is None:
                continue
            for trace in trace_fig.data:
                label = PydanticChartEditor._entry_display_name(chart_entry)
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
