from dash_chart_editor.aio.px_metadata import PX_CHART_METADATA


def test_scatter_metadata_contains_common_kwargs():
    scatter = PX_CHART_METADATA["scatter"]
    assert "x" in scatter["kwargs"]
    assert "y" in scatter["kwargs"]
    assert "x" in scatter["column_kwargs"] or "x" in scatter["multi_column_kwargs"]
    assert "y" in scatter["column_kwargs"] or "y" in scatter["multi_column_kwargs"]


def test_pie_metadata_detects_column_kwargs():
    pie = PX_CHART_METADATA["pie"]
    assert "names" in pie["column_kwargs"]
    assert "values" in pie["column_kwargs"]
