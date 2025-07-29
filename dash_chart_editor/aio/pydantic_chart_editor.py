from dash import html, dcc, callback, Output, Input, State, MATCH, ctx
import plotly.express as px
import plotly.graph_objs as go
from dash_pydantic_form import ModelForm, TabsFormLayout, FormSection
from pydantic import BaseModel, Field, create_model
from typing import List, Optional, Dict, Any, Literal
import dash_mantine_components as dmc
import inspect
import pandas as pd
import re
import json

df_cols = ['color', 'size', 'x', 'y', 'z', 'values', 'labels', 'lat', 'lon', 'path',
           'facet_row', 'facet_col']

exclude = ['template', 'width', 'height', 'title']

def infer_param_type(param, param_obj, doc):
    # Try to get type from annotation
    if param_obj.annotation != inspect.Parameter.empty:
        return param_obj.annotation
    # Try to infer from default value
    if param_obj.default != inspect.Parameter.empty and param_obj.default is not None:
        return type(param_obj.default)
    # Fallback: parse docstring for type
    match = re.search(rf"{param}\s*:\s*([^\n]+)", doc)
    if param in df_cols:
        if param == 'path':
            return list
        return str
    if match:
        doc_type = match.group(1).split(',')[0].strip().lower()
        # Map common docstring types to Python types
        if 'str' in doc_type or 'string' in doc_type:
            return str
        if 'int' in doc_type or 'integer' in doc_type:
            return int
        if 'float' in doc_type or 'number' in doc_type:
            return float
        if 'bool' in doc_type or 'boolean' in doc_type:
            return bool
        if 'list' in doc_type or 'array' in doc_type:
            return list
        if 'dict' in doc_type or 'mapping' in doc_type:
            return dict
    # Default fallback
    return str

def get_px_chart_options():
    chart_options = {}
    for chart_name in px.__all__:
        chart_func = getattr(px, chart_name)
        if callable(chart_func):
            sig = inspect.signature(chart_func)
            # Exclude 'data_frame' and 'args'/'kwargs'
            params = [
                p.name for p in sig.parameters.values()
                if p.name != 'data_frame' and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
            ]
            chart_options[chart_name] = params
    return chart_options

def classify_px_args_with_types():
    major_keywords = ['data', 'column', 'axis', 'group', 'value', 'label', 'category', 'dimension']
    chart_options = get_px_chart_options()
    major_args = {}
    style_args = {}
    facet_args = {}

    for chart_name, params in chart_options.items():
        chart_func = getattr(px, chart_name)
        doc = chart_func.__doc__ or ""
        sig = inspect.signature(chart_func)
        for param in params:
            param_obj = sig.parameters.get(param)
            param_type = infer_param_type(param, param_obj, doc)
            match = re.search(rf"{param}\s*:\s*.*?\n\s+(.*?)(?=\n\S|$)", doc, re.DOTALL)
            desc = match.group(1).lower() if match else ""
            if param in exclude:
                continue
            if 'facet' in param:
                facet_args[param] = param_type
            elif param in ['color', 'size', 'x', 'y', 'z', 'values', 'labels', 'lat', 'lon', 'path']:
                major_args[param] = param_type
            else:
                style_args[param] = param_type
    return major_args, style_args, facet_args

major_props, style_props, facet_props = classify_px_args_with_types()

from enum import Enum
# Dynamically get all trace types from plotly.graph_objs
def get_trace_types():
    return [
        name for name in px.__all__
    ]

# Create an Enum for chart types
ChartTypeEnum = Enum(
    "ChartTypeEnum",
    {name.lower(): name.lower() for name in get_trace_types()}
)


def render_chart(form_data, df):
    traces = form_data["structure"].get("traces", [])
    # Check for facet usage
    facet_charts = [
        chart for chart in traces
        if chart.get("facet", {}).get('facet_row') or chart.get("facet", {}).get('facet_col')
    ]
    if facet_charts and len(traces) > 1:
        raise ValueError("Only one chart is supported when using facets (facet_row or facet_col).")

    fig = go.Figure()
    for chart in traces:
        chart_type = chart.get("name")
        trace_args = chart.copy()
        trace_args.pop("name", None)
        px_func = getattr(px, chart_type)
        major_args = chart.get("major", {}) or {}
        style_args = chart.get("style", {}) or {}
        facet_args = chart.get("facet", {}) or {}
        valid_fields = set(PX_FIELD_VISIBILITY.get(chart_type, []))
        # Merge and filter by valid fields and non-None values
        px_args = {k: v for k, v in {**major_args, **style_args, **facet_args}.items() if k in valid_fields and v is not None and v != ""}
        px_fig = px_func(df, **px_args)
        for trace in px_fig.data:
            fig.add_trace(trace)
        if facet_charts:
            # If facets are used, we only take the first chart's layout
            fig.update_layout(px_fig.layout)
            break

    layout = form_data.get("layout", {})
    fig.update_layout(
        title=layout.get("title", ""),
        height=layout.get("height", 600),
        width=layout.get("width", 900)
    )

    for ann in form_data.get("annotations", []):
        fig.add_annotation(
            text=ann.get("text", ""),
            x=ann.get("x", 0),
            y=ann.get("y", 0),
            showarrow=True
        )

    return fig

import inspect

PX_FIELD_VISIBILITY = get_px_chart_options()

def visible_for_field(field_name):
    # List all chart types that support this field
    valid_charts = [k for k, v in PX_FIELD_VISIBILITY.items() if field_name in v]
    return [('_parent_:name', 'in', valid_charts)]

def make_field(k, v, df):
    if k in df_cols:
        # Restrict to columns in df
        if df is None or df.empty:
            return (Optional[v], Field(None, title=k.replace('_', ' ').title(), repr_kwargs=dict(visible=visible_for_field(k))))

        choices = tuple(df.columns) if df is not None else ()
        if k == 'path':
            # For 'path', allow multiple selections from df columns
            if choices:
                return (
                    List[Literal[choices]],
                    Field(
                        None,
                        title=k.replace('_', ' ').title(),
                        repr_kwargs=dict(visible=visible_for_field(k)),
                        fields_repr={"type": "MultiSelect"}
                    )
                )
            else:
                return (
                    Optional[List[str]],
                    Field(
                        None,
                        title=k.replace('_', ' ').title(),
                        repr_kwargs=dict(visible=visible_for_field(k)),
                        fields_repr={"type": "MultiSelect"}
                    )
                )
        return (Literal[choices],
                Field(None, title=k.replace('_', ' ').title(),
                      repr_kwargs=dict(visible=visible_for_field(k))))
    else:
        return (Optional[v], Field(None, title=k.replace('_', ' ').title(), repr_kwargs=dict(visible=visible_for_field(k))))

def CreateChartModel(aio_id, df, old_data):
    # Build fields for major and style props
    major_fields = {k: make_field(k, v, df) for k, v in major_props.items()}
    style_fields = {k: make_field(k, v, df) for k, v in style_props.items()}
    facet_fields = {k: make_field(k, v, df) for k, v in facet_props.items()}

    # Create models
    MajorChartConfig = create_model('MajorChartConfig', **major_fields)
    StyleChartConfig = create_model('StyleChartConfig', **style_fields)
    FacetChartConfig = create_model('FacetChartConfig', **facet_fields)

    # Optionally, combine them in a parent model
    ChartConfig = create_model(
        'ChartConfig',
        name=(ChartTypeEnum, Field(..., title="Chart Type", repr_kwargs={"searchable": True})),
        major=(MajorChartConfig, Field(...,title="Common Chart Properties")),
        style=(StyleChartConfig, Field(..., title="Other Chart Properties", input_kwargs={"default_open": False})),
        facet=(Optional[FacetChartConfig], Field(None, title="Facet Properties", input_kwargs={"default_open": False})),
    )

    class LayoutConfig(BaseModel):
        title: Optional[str] = Field(None, title="Figure Title")
        height: Optional[int] = Field(600, title="Height")
        width: Optional[int] = Field(900, title="Width")

    class AnnotationConfig(BaseModel):
        text: str = Field(..., title="Text")
        x: float = Field(..., title="X Position")
        y: float = Field(..., title="Y Position")

    class StructureOptions(BaseModel):
        subplots: bool = Field(True, title="Subplots")
        traces: List[ChartConfig] = Field(title="Charts")
        transforms: bool = Field(False, title="Transforms")

    class EditorFormModel(BaseModel):
        structure: StructureOptions
        layout: Optional[LayoutConfig] = Field(default_factory=LayoutConfig, title="Layout")
        annotations: List[AnnotationConfig] = Field(default_factory=list, title="Annotations")

    if old_data:
        # Use old_data to populate the model if available
        new_form = EditorFormModel(**old_data)
    else:
        new_form = EditorFormModel

    model_from = ModelForm(
        new_form,
        aio_id=aio_id,
        form_id='pydantic-chart-editor-form',
        form_layout=TabsFormLayout(
            sections=[
                FormSection(
                    name="Structure",
                    fields=[
                        "structure",
                        # "transforms"
                    ]
                ),
                FormSection(
                    name="Style",
                    fields=[
                        "layout",
                    ]
                ),
                FormSection(
                    name="Annotate",
                    fields=[
                        "annotations",
                        # "text",
                        # "shapes",
                        # "images"
                    ]
                )
            ],
            render_kwargs={"orientation": "vertical"}
        )
    )

    return model_from

class PydanticChartEditorAIO:
    class ids:
        @staticmethod
        def form(aio_id): return {"component": "PydanticChartEditorAIO", "subcomponent": "form", "aio_id": aio_id}
        @staticmethod
        def chart(aio_id): return {"component": "PydanticChartEditorAIO", "subcomponent": "chart", "aio_id": aio_id}
        @staticmethod
        def debug(aio_id): return {"component": "PydanticChartEditorAIO", "subcomponent": "debug", "aio_id": aio_id}
        @staticmethod
        def data_source(aio_id): return {"component": "PydanticChartEditorAIO", "subcomponent": "data_source", "aio_id": aio_id}
        @staticmethod
        def button(aio_id): return {"component": "PydanticChartEditorAIO", "subcomponent": "submit_button",
                                         "aio_id": aio_id}

    def __init__(self, aio_id, data_sources: Dict[str, Any]):
        self.aio_id = aio_id
        self.data_sources = data_sources

    def layout(self):
        return html.Div([
            html.Div([
                dcc.Dropdown(
                    id=self.ids.data_source(self.aio_id),
                    options=[{"label": k, "value": k} for k in self.data_sources.keys()],
                    value=next(iter(self.data_sources.keys()), None),
                    placeholder="Select data source"
                ),
                html.H4("Pydantic Chart Editor"),
                html.Div(
                    id=self.ids.form(self.aio_id)
                ),
                dmc.Button('Update Chart', id=self.ids.button(self.aio_id), n_clicks=0, variant='outline'),
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                dcc.Graph(id=self.ids.chart(self.aio_id), style={'height': '600px'}),
                html.Div(id=self.ids.debug(self.aio_id))
            ], style={'width': '68%', 'display': 'inline-block', 'marginLeft': '2%'})
        ])

    @callback(
        Output(ids.form(MATCH), "children"),
        Input(ids.data_source(MATCH), "value"),
        State(ModelForm.ids.main(MATCH, 'pydantic-chart-editor-form'), "data", allow_optional=True),
        State(ids.form(MATCH), "id"),
    )
    def update_form(data, form_data, id):
        from dash_chart_editor.aio.pydantic_chart_editor import PydanticChartEditorAIO
        data_sources = getattr(PydanticChartEditorAIO, "_data_sources", {})
        return CreateChartModel(
            aio_id=id['aio_id'],
            df=pd.DataFrame(data_sources[data]) if data else None,
            old_data = json.loads(form_data) if isinstance(form_data, str) and form_data else (form_data or {})
        )

    @callback(
        Output(ids.chart(MATCH), "figure"),
        Output(ids.debug(MATCH), "children"),
        Input(ids.button(MATCH), "n_clicks"),
        State(ModelForm.ids.main(MATCH, 'pydantic-chart-editor-form'), "data"),
        State(ids.data_source(MATCH), "value"),
        prevent_initial_call=True
    )
    def update_chart(n, form_data, data_source):
        from dash_chart_editor.aio.pydantic_chart_editor import PydanticChartEditorAIO
        data_sources = getattr(PydanticChartEditorAIO, "_data_sources", {})
        if not form_data or not data_source or data_source not in data_sources:
            return go.Figure(), "Waiting for form data and data source..."
        df = data_sources[data_source]

        return render_chart(form_data, df), f"Form data: {form_data}"