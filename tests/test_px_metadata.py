from dash_chart_editor.aio.px_metadata import PX_CHART_METADATA, FIXED_OPTIONS


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
