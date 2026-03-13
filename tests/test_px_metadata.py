from dash_chart_editor.aio.px_metadata import PX_CHART_METADATA, FIXED_OPTIONS, NUMERIC_CONSTRAINTS


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


def test_numeric_constraints_defined():
    """NUMERIC_CONSTRAINTS should include common numeric params."""
    assert "opacity" in NUMERIC_CONSTRAINTS
    assert NUMERIC_CONSTRAINTS["opacity"]["type"] == float
    assert NUMERIC_CONSTRAINTS["opacity"]["ge"] == 0.0
    assert NUMERIC_CONSTRAINTS["opacity"]["le"] == 1.0
    assert "facet_col_wrap" in NUMERIC_CONSTRAINTS
    assert NUMERIC_CONSTRAINTS["facet_col_wrap"]["type"] == int
