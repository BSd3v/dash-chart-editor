from dash_chart_editor.aio.px_metadata import PX_CHART_METADATA, FIXED_OPTIONS, NUMERIC_CONSTRAINTS, MAX_DESCRIPTION_LENGTH
from dash_chart_editor.aio.pydantic_chart_editor import (
    _RELAYOUT_TO_LAYOUT, _PX_API_BASE, PydanticChartEditor,
)


def test_scatter_metadata_contains_common_kwargs():
    scatter = PX_CHART_METADATA["scatter"]
    assert "x" in scatter["kwargs"]
    assert "y" in scatter["kwargs"]
    assert "x" in scatter["column_kwargs"]
    assert "y" in scatter["column_kwargs"]
    assert "x" not in scatter["multi_column_kwargs"]
    assert "y" not in scatter["multi_column_kwargs"]


def test_pie_metadata_detects_column_kwargs():
    pie = PX_CHART_METADATA["pie"]
    assert "names" in pie["column_kwargs"]
    assert "values" in pie["column_kwargs"]


def test_make_figure_not_in_metadata():
    assert "make_figure" not in PX_CHART_METADATA
    assert "make_docstring" not in PX_CHART_METADATA


def test_fixed_options_detected():
    assert "trendline" in FIXED_OPTIONS
    assert "marginal_x" in FIXED_OPTIONS
    assert isinstance(FIXED_OPTIONS["trendline"], list)
    assert len(FIXED_OPTIONS["trendline"]) > 0


def test_scatter_has_fixed_options_in_metadata():
    scatter = PX_CHART_METADATA["scatter"]
    fo = scatter.get("fixed_options", {})
    # trendline is a fixed-option param for scatter
    assert "trendline" in fo


def test_orientation_options_only_h_v():
    """orientation should only include 'h' and 'v', not 'x' or 'y'."""
    opts = FIXED_OPTIONS.get("orientation", [])
    assert "h" in opts
    assert "v" in opts
    assert "x" not in opts, "'x' is a column ref, not a valid orientation"
    assert "y" not in opts, "'y' is a column ref, not a valid orientation"


def test_param_defaults_captured():
    """Metadata should include param_defaults with signature defaults."""
    scatter = PX_CHART_METADATA["scatter"]
    defaults = scatter.get("param_defaults", {})
    # log_x and log_y default to False in px.scatter
    assert "log_x" in defaults
    assert defaults["log_x"] is False


def test_param_descriptions_captured():
    """Metadata should include param_descriptions with short doc text."""
    scatter = PX_CHART_METADATA["scatter"]
    descs = scatter.get("param_descriptions", {})
    assert isinstance(descs, dict)
    assert "x" in descs
    assert len(descs["x"]) > 0
    assert len(descs["x"]) <= MAX_DESCRIPTION_LENGTH


def test_numeric_constraints_defined():
    """NUMERIC_CONSTRAINTS should include common numeric params with correct constraints."""
    assert "opacity" in NUMERIC_CONSTRAINTS
    assert NUMERIC_CONSTRAINTS["opacity"]["type"] == float
    assert NUMERIC_CONSTRAINTS["opacity"]["ge"] == 0.0
    assert NUMERIC_CONSTRAINTS["opacity"]["le"] == 1.0
    # Float fields use multiple_of (not step/json_schema_extra) so pydf reads it from
    # field_info.metadata as annotated_types.MultipleOf → NumberInput step attribute.
    assert NUMERIC_CONSTRAINTS["opacity"]["multiple_of"] == 0.1
    assert "facet_col_wrap" in NUMERIC_CONSTRAINTS
    assert NUMERIC_CONSTRAINTS["facet_col_wrap"]["type"] == int
    # int params should NOT have multiple_of (they step by 1 by default)
    assert "multiple_of" not in NUMERIC_CONSTRAINTS["facet_col_wrap"]


def test_numeric_field_metadata_in_pydantic_model():
    """multiple_of in NUMERIC_CONSTRAINTS should appear in pydantic field_info.metadata."""
    import annotated_types

    model = PydanticChartEditor._build_form_model("scatter", ["a", "b"], set())
    fi = model.model_fields.get("opacity")
    assert fi is not None
    steps = [m.multiple_of for m in fi.metadata if isinstance(m, annotated_types.MultipleOf)]
    assert steps == [0.1], f"Expected step=0.1 in field_info.metadata, got: {fi.metadata}"


def test_relayout_to_layout_map():
    """_RELAYOUT_TO_LAYOUT should include key layout fields."""
    assert "title.text" in _RELAYOUT_TO_LAYOUT
    assert _RELAYOUT_TO_LAYOUT["title.text"] == "title"
    assert "legend.x" in _RELAYOUT_TO_LAYOUT
    assert "paper_bgcolor" in _RELAYOUT_TO_LAYOUT
    assert "showlegend" in _RELAYOUT_TO_LAYOUT


def test_show_doc_link_parameter_stored():
    """PydanticChartEditor should accept show_doc_link=False and expose it as a public attribute."""
    import pandas as pd
    editor = PydanticChartEditor(
        data_sources={"df": pd.DataFrame({"a": [1, 2], "b": [3, 4]})},
        component_id="test-linked",
        show_doc_link=False,
    )
    assert editor.show_doc_link is False


def test_doc_link_url_format():
    """_PX_API_BASE should produce the correct Plotly API reference URL."""
    url = _PX_API_BASE.format("scatter")
    assert "plotly.com/python-api-reference" in url
    assert "scatter" in url
    assert url.endswith(".html")
