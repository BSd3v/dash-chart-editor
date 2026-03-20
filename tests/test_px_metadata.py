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


def test_unified_editor_state_model():
    """_EditorState should combine a list of _ChartEntry with a _LayoutConfig."""
    from dash_chart_editor.aio.pydantic_chart_editor import (
        _EditorState, _ChartEntry, _LayoutConfig,
    )

    state = _EditorState(
        charts=[
            _ChartEntry(label="A", chart_type="scatter", data_source="ds", x="x", y="y"),
            _ChartEntry(label="B", chart_type="bar", data_source="ds", x="cat", y="val"),
        ],
        shared_layout=_LayoutConfig(title="Combined", showlegend=True),
    )
    assert len(state.charts) == 2
    assert state.charts[0].label == "A"
    assert state.charts[1].chart_type == "bar"
    assert state.shared_layout.title == "Combined"
    assert state.shared_layout.showlegend is True


def test_chart_entry_column_fields_in_model():
    """_ChartEntry should expose standard column fields (x, y, color, size, names, values)."""
    from dash_chart_editor.aio.pydantic_chart_editor import _ChartEntry

    entry = _ChartEntry(chart_type="pie", data_source="ds", names="category", values="amount")
    assert entry.names == "category"
    assert entry.values == "amount"
    assert entry.x is None
    assert entry.y is None


def test_layout_config_paper_plot_bgcolor():
    """_LayoutConfig should include paper_bgcolor and plot_bgcolor fields."""
    from dash_chart_editor.aio.pydantic_chart_editor import _LayoutConfig

    layout = _LayoutConfig(paper_bgcolor="white", plot_bgcolor="#f0f0f0")
    assert layout.paper_bgcolor == "white"
    assert layout.plot_bgcolor == "#f0f0f0"
    # Ensure they are in _RELAYOUT_TO_LAYOUT
    assert "paper_bgcolor" in _RELAYOUT_TO_LAYOUT
    assert "plot_bgcolor" in _RELAYOUT_TO_LAYOUT


def test_dynamic_chart_union_models_built_from_px():
    """Editor should build per-chart models dynamically from PX_CHART_METADATA."""
    from dash_chart_editor.aio.pydantic_chart_editor import get_chart_union_models

    models = get_chart_union_models()
    assert isinstance(models, list)
    assert len(models) == len(PX_CHART_METADATA)

    names = {m.__name__ for m in models}
    assert "ScatterChartEntry" in names
    assert "PieChartEntry" in names


def test_dynamic_editor_state_accepts_chart_union_entries():
    """_EditorState should validate entries against union models (not only _ChartEntry)."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState

    state = _EditorState.model_validate(
        {
            "charts": [
                {
                    "label": "S1",
                    "chart_type": "scatter",
                    "data_source": "Iris",
                    "x": "sepal_length",
                    "y": "sepal_width",
                },
                {
                    "label": "P1",
                    "chart_type": "pie",
                    "data_source": "Tips",
                    "names": "day",
                    "values": "total_bill",
                },
            ],
            "shared_layout": {"title": "Combined"},
        }
    )
    assert len(state.charts) == 2
    assert state.charts[0].chart_type == "scatter"
    assert state.charts[1].chart_type == "pie"
    assert state.shared_layout.title == "Combined"
