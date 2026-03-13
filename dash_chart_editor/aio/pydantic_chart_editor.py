"""Standalone chart editor backed by dash-pydantic-form."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Literal, Optional, Set

import dash
from dash import dcc, html, callback, Output, Input, State, MATCH, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
from pydantic import BaseModel, Field, create_model

from dash_pydantic_form import ModelForm

from .px_metadata import PX_CHART_METADATA, NUMERIC_CONSTRAINTS

_PYDF_FORM_ID = "pydantic-chart-editor-form"
_PYDF_LAYOUT_FORM_ID = "pydantic-chart-layout-form"
_SHARED_LAYOUT_KEY = "__shared_layout__"

# Plotly Express API reference URL pattern — used to build chart-type-specific doc links.
# These mirror the links shown in Dashboard-Helper's "Chart Info" panel.
_PX_API_BASE = "https://plotly.com/python-api-reference/generated/plotly.express.{}.html"
_PX_EXAMPLES_URL = "https://plotly.com/python/"
_LAYOUT_REF_URL = (
    "https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html"
)

# Maps Plotly relayoutData keys → _LayoutConfig field names.
# In-graph edits (title, legend position, background color, etc.) are synced back to the
# layout form via the sync_relayout_to_form callback so the form and chart stay in step.
# Axis-specific keys such as ``xaxis.title.text`` are handled separately by
# _apply_relayout (which applies them directly to the figure) rather than through the
# layout form, since the layout form does not have individual axis title fields.
_RELAYOUT_TO_LAYOUT: dict[str, str] = {
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

    title: Optional[str] = Field(default=None, title="Title",
                                  description="The chart title displayed above the plot.")
    height: Optional[int] = Field(default=None, title="Height (px)",
                                   description="Height of the figure in pixels.", ge=100)
    width: Optional[int] = Field(default=None, title="Width (px)",
                                  description="Width of the figure in pixels.", ge=100)
    showlegend: Optional[bool] = Field(default=None, title="Show Legend",
                                        description="Whether to show the legend.")
    legend_x: Optional[float] = Field(default=None, title="Legend X Position (0–1)",
                                       description="Horizontal position of the legend (0=left, 1=right).",
                                       ge=0.0, le=1.0, multiple_of=0.1)
    legend_y: Optional[float] = Field(default=None, title="Legend Y Position (0–1)",
                                       description="Vertical position of the legend (0=bottom, 1=top).",
                                       ge=0.0, le=1.0, multiple_of=0.1)
    legend_orientation: Optional[Literal["v", "h"]] = Field(default=None, title="Legend Orientation",
                                                              description="'v' for vertical, 'h' for horizontal.")
    legend_xanchor: Optional[Literal["auto", "left", "center", "right"]] = Field(
        default=None, title="Legend X Anchor",
        description="Horizontal anchor point for the legend position.")
    legend_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]] = Field(
        default=None, title="Legend Y Anchor",
        description="Vertical anchor point for the legend position.")
    template: Optional[str] = Field(default=None, title="Template",
                                   description="Plotly template to use for styling the chart.")


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

        @staticmethod
        def doc_link_container(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "doc_link_container", "aio_id": aio_id}

        @staticmethod
        def chart_select(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "chart_select", "aio_id": aio_id}

        @staticmethod
        def add_chart_btn(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "add_chart_btn", "aio_id": aio_id}

        @staticmethod
        def remove_chart_btn(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "remove_chart_btn", "aio_id": aio_id}

        @staticmethod
        def chart_states(aio_id):
            return {"component": "PydanticChartEditor", "subcomponent": "chart_states", "aio_id": aio_id}

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
            data_sources: Named DataFrames to populate column selectors.
            component_id: Unique component identifier. Auto-generated if not provided.
            excluded_kwargs: Set of chart kwarg names to hide from the form.  The developer
                can use this to simplify the editor for their users (e.g. hide ``trendline``,
                ``facet_row``, etc.).
            show_doc_link: When ``True`` (default), a "Chart Info" panel is shown below the
                chart-type selector with links to the Plotly API reference for the selected
                chart type, Plotly example docs, and the layout reference — matching the
                Dashboard-Helper behaviour.  Set to ``False`` to hide these links.
            multi_chart: When ``True`` (default), enables chart management controls (add/remove/
                select chart) and stores separate chart state per selected chart, similar to RCE.
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

    @property
    def chart_options(self):
        return [{"label": name, "value": name} for name in sorted(PX_CHART_METADATA.keys())]

    def _build_layout(self):
        option_values = [item["value"] for item in self.chart_options]
        default_chart = "scatter" if "scatter" in option_values else (option_values[0] if option_values else None)
        data_source_options = [{"label": name, "value": name} for name in self.data_sources]
        default_data = data_source_options[0]["value"] if data_source_options else None
        initial_chart_states = {
            "Chart 1": {
                "chart_type": default_chart,
                "data_source": default_data,
                "form_data": {},
            },
            _SHARED_LAYOUT_KEY: {},
        }

        return [
            dmc.MantineProvider(
                html.Div(
                    [
                        html.H4("Chart Editor", style={"marginBottom": "20px"}),
                        dmc.Accordion(
                            children=[
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl("Charts"),
                                        dmc.AccordionPanel(
                                            [
                                                html.Label("Chart Type"),
                                                html.Div(
                                                    [
                                                        html.Label("Charts", style={"marginBottom": "4px"}),
                                                        dcc.Dropdown(
                                                            id=self.ids.chart_select(self.component_id),
                                                            options=[{"label": "Chart 1", "value": "Chart 1"}],
                                                            value="Chart 1",
                                                            clearable=False,
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Button("Add", id=self.ids.add_chart_btn(self.component_id),
                                                                            style={"marginRight": "8px"}),
                                                                html.Button("Remove", id=self.ids.remove_chart_btn(self.component_id)),
                                                            ],
                                                            style={"marginTop": "8px"},
                                                        ),
                                                    ],
                                                    style={} if self.multi_chart else {"display": "none"},
                                                ),
                                                dcc.Dropdown(
                                                    id=self.ids.chart_type(self.component_id),
                                                    options=self.chart_options,
                                                    value=default_chart,
                                                    clearable=False,
                                                ),
                                                html.Div(
                                                    id=self.ids.doc_link_container(self.component_id),
                                                    style={"marginTop": "6px", "fontSize": "12px"}
                                                    if self.show_doc_link
                                                    else {"display": "none"},
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
                                            ]
                                        ),
                                    ],
                                    value="charts",
                                ),
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl("Layout"),
                                        dmc.AccordionPanel(
                                            [
                                                html.H6("Layout", style={"marginBottom": "8px"}),
                                                ModelForm(item=_LayoutConfig, aio_id=self.component_id,
                                                          form_id=_PYDF_LAYOUT_FORM_ID),
                                            ]
                                        ),
                                    ],
                                    value="layout",
                                ),
                            ],
                            value=["charts", "layout"],
                            multiple=True,
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
                    dcc.Store(id=self.ids.chart_states(self.component_id), data=initial_chart_states),
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
        # Drop None, empty strings, and empty lists — all represent "not set" in the form UI
        clean_kwargs = {
            k: v for k, v in chart_kwargs.items()
            if v is not None and v != "" and v != []
        }
        return chart_fn(data_frame=data_frame, **clean_kwargs)

    @staticmethod
    def _build_form_model(chart_type: str, columns: List[str], excluded: Set[str]) -> type[BaseModel]:
        metadata = PX_CHART_METADATA[chart_type]
        column_kwargs = set(metadata["column_kwargs"])
        multi_column_kwargs = set(metadata["multi_column_kwargs"])
        fixed_options: dict[str, list[str]] = metadata.get("fixed_options", {})
        param_defaults: dict[str, Any] = metadata.get("param_defaults", {})
        param_descriptions: dict[str, str] = metadata.get("param_descriptions", {})

        fields: dict[str, tuple[Any, Any]] = {}
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

            # Fixed options → use Literal so ModelForm renders a Select dropdown.
            # Pre-select the signature default if it appears in the valid options.
            if arg in fixed_options:
                opts = tuple(dict.fromkeys(fixed_options[arg]))  # preserve unique values in original order
                if opts:
                    field_type = Optional[Literal[opts]]  # type: ignore[valid-type]
                    # Use the signature default when it's a valid option; otherwise None
                    field_default = sig_default if isinstance(sig_default, str) and sig_default in opts else None
                    fields[arg] = (field_type, Field(default=field_default, title=title, description=desc or None))
                    continue

            # Numeric params: pass ge/le/multiple_of directly on the outer Field() so they
            # end up in field_info.metadata as annotated_types.Ge/Le/MultipleOf objects.
            # dash-pydantic-form reads those objects to set min/max/step on the NumberInput.
            if arg in NUMERIC_CONSTRAINTS:
                nc = NUMERIC_CONSTRAINTS[arg]
                num_type = nc["type"]
                field_kwargs: dict[str, Any] = {"title": title}
                if desc:
                    field_kwargs["description"] = desc
                if "ge" in nc:
                    field_kwargs["ge"] = nc["ge"]
                if "le" in nc:
                    field_kwargs["le"] = nc["le"]
                if "multiple_of" in nc:
                    # multiple_of → annotated_types.MultipleOf in field_info.metadata
                    # pydf's NumberField._additional_kwargs reads this as the step attribute
                    field_kwargs["multiple_of"] = nc["multiple_of"]
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
            fields[arg] = (field_type, Field(default=None, title=title, description=desc or None))

        return create_model(f"{chart_type.title()}Form", **fields)

    # ── Auto-wired AIO callbacks ──────────────────────────────────────────────

    @staticmethod
    @callback(
        Output(ids.chart_select(MATCH), "options"),
        Output(ids.chart_select(MATCH), "value"),
        Output(ids.chart_states(MATCH), "data"),
        Input(ids.add_chart_btn(MATCH), "n_clicks"),
        Input(ids.remove_chart_btn(MATCH), "n_clicks"),
        State(ids.chart_select(MATCH), "value"),
        State(ids.chart_states(MATCH), "data"),
        prevent_initial_call=True,
    )
    def manage_charts(add_clicks, remove_clicks, selected_chart, chart_states):
        """Manage add/remove/select chart in multi-chart mode."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update

        states = dict(chart_states or {})
        shared_layout = dict(states.get(_SHARED_LAYOUT_KEY, {}))
        chart_keys = [k for k in states.keys() if k != _SHARED_LAYOUT_KEY]
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        is_add = '"subcomponent":"add_chart_btn"' in trigger
        is_remove = '"subcomponent":"remove_chart_btn"' in trigger

        if is_add:
            idx = len(chart_keys) + 1
            while f"Chart {idx}" in states:
                idx += 1
            new_name = f"Chart {idx}"
            states[new_name] = {"chart_type": "scatter", "data_source": None, "form_data": {}}
            selected = new_name
        elif is_remove and selected_chart and selected_chart in states:
            states.pop(selected_chart, None)
            chart_keys = [k for k in states.keys() if k != _SHARED_LAYOUT_KEY]
            if not chart_keys:
                states["Chart 1"] = {"chart_type": "scatter", "data_source": None, "form_data": {}}
                chart_keys = ["Chart 1"]
            selected = chart_keys[0]
        else:
            return no_update, no_update, no_update

        states[_SHARED_LAYOUT_KEY] = shared_layout
        options = [{"label": name, "value": name} for name in states.keys() if name != _SHARED_LAYOUT_KEY]
        return options, selected, states

    @staticmethod
    @callback(
        Output(ids.chart_type(MATCH), "value"),
        Output(ids.data_source(MATCH), "value"),
        Input(ids.chart_select(MATCH), "value"),
        State(ids.chart_states(MATCH), "data"),
        State(ids.data_source(MATCH), "options"),
        prevent_initial_call=True,
    )
    def load_selected_chart(selected_chart, chart_states, data_source_options):
        """Load chart_type/data_source for currently selected logical chart."""
        states = chart_states or {}
        cfg = states.get(selected_chart or "", {})
        chart_type = cfg.get("chart_type") or "scatter"
        ds_value = cfg.get("data_source")
        if ds_value is None and data_source_options:
            ds_value = data_source_options[0]["value"]
        return chart_type, ds_value

    @staticmethod
    @callback(
        Output(ModelForm.ids.form(MATCH, _PYDF_FORM_ID), "data-update", allow_duplicate=True),
        Output(ModelForm.ids.form(MATCH, _PYDF_LAYOUT_FORM_ID), "data-update", allow_duplicate=True),
        Input(ids.chart_select(MATCH), "value"),
        State(ids.chart_states(MATCH), "data"),
        prevent_initial_call=True,
    )
    def load_selected_chart_forms(selected_chart, chart_states):
        """Load stored chart/layout form state when switching selected chart."""
        states = chart_states or {}
        cfg = states.get(selected_chart or "", {})
        shared_layout = states.get(_SHARED_LAYOUT_KEY, {})
        return cfg.get("form_data", {}), shared_layout

    @staticmethod
    @callback(
        Output(ids.chart_states(MATCH), "data", allow_duplicate=True),
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data", allow_optional=True),
        Input(ModelForm.ids.main(MATCH, _PYDF_LAYOUT_FORM_ID), "data", allow_optional=True),
        Input(ids.chart_type(MATCH), "value"),
        Input(ids.data_source(MATCH), "value"),
        State(ids.chart_select(MATCH), "value"),
        State(ids.chart_states(MATCH), "data"),
        prevent_initial_call=True,
    )
    def persist_selected_chart_state(form_data, layout_data, chart_type, data_source, selected_chart, chart_states):
        """Persist current selected chart state so multiple charts are supported."""
        if not selected_chart:
            return no_update
        states = dict(chart_states or {})
        if layout_data:
            states[_SHARED_LAYOUT_KEY] = layout_data
        cfg = dict(states.get(selected_chart, {}))
        cfg["chart_type"] = chart_type
        cfg["data_source"] = data_source
        cfg["form_data"] = form_data or {}
        states[selected_chart] = cfg
        return states

    @staticmethod
    @callback(
        Output(ids.doc_link_container(MATCH), "children"),
        Input(ids.chart_type(MATCH), "value"),
    )
    def update_doc_links(chart_type):
        """Update the documentation links panel when the chart type changes.

        Mirrors the "Chart Info" accordion panel in Dashboard-Helper, providing
        direct links to the Plotly API reference for the selected chart type,
        the general Plotly example docs, and the layout reference.  The container
        is hidden when ``show_doc_link=False`` (via CSS display:none), so this
        callback fires either way but the output is never visible when disabled.
        """
        if not chart_type:
            return []
        api_url = _PX_API_BASE.format(chart_type)
        link_style = {"color": "#7575dd", "marginRight": "8px", "textDecoration": "none"}
        return html.Div(
            [
                html.Span("📖 "),
                html.A("API Reference", href=api_url, target="_blank", style=link_style),
                html.Span("·", style={"marginRight": "8px", "color": "#aaa"}),
                html.A("Example Docs", href=_PX_EXAMPLES_URL, target="_blank", style=link_style),
                html.Span("·", style={"marginRight": "8px", "color": "#aaa"}),
                html.A("Layout Reference", href=_LAYOUT_REF_URL, target="_blank", style=link_style),
            ],
            style={"padding": "4px 0"},
        )

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
        return ModelForm(
            item=model,
            aio_id=aio_id,
            form_id=PydanticChartEditor._FORM_ID,
        )

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
        Input(ModelForm.ids.main(MATCH, _PYDF_FORM_ID), "data", allow_optional=True),
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
    @callback(
        Output(ModelForm.ids.form(MATCH, _PYDF_LAYOUT_FORM_ID), "data-update"),
        Input(ids.chart(MATCH), "relayoutData"),
        State(ModelForm.ids.main(MATCH, _PYDF_LAYOUT_FORM_ID), "data"),
        prevent_initial_call=True,
    )
    def sync_relayout_to_form(relayout_data, current_layout_data):
        """Sync in-graph edits (title, legend, bgcolor, etc.) back to the layout form.

        Plotly fires ``relayoutData`` whenever the user edits a chart element directly
        (e.g. clicks the title to rename it, drags the legend, changes background colour).
        This callback maps the changed keys to the corresponding ``_LayoutConfig`` fields
        via ``_RELAYOUT_TO_LAYOUT`` and updates the layout form store so the form and
        chart stay in step.  Keys not in the map (e.g. axis-specific settings, zoom/pan
        range changes) are intentionally ignored here — ``_apply_relayout`` handles those
        directly on the figure object instead.
        """
        if relayout_data is None or not relayout_data:
            return no_update

        updated = dict(current_layout_data or {})
        changed = False
        for relayout_key, layout_key in _RELAYOUT_TO_LAYOUT.items():
            if relayout_key in relayout_data:
                updated[layout_key] = relayout_data[relayout_key]
                changed = True

        return updated if changed else no_update

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
                # Skip blank/unset values — None, empty string, or empty list all mean "not set"
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

            # Re-apply any in-graph user edits (title, axis labels, annotations, etc.)
            # relayoutData contains only the delta of changes made by the user in the graph.
            # This covers relayout keys not captured by the layout form (e.g. axis tick settings,
            # annotations).  The layout form already has the synced values for keys in
            # _RELAYOUT_TO_LAYOUT (via sync_relayout_to_form), so _apply_relayout is harmless
            # for those — but it's a necessary fallback for all other relayout keys.
            if relayout_data is not None and relayout_data:
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
