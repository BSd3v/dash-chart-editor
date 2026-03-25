from dash_chart_editor.aio.px_metadata import (
    PX_CHART_METADATA, FIXED_OPTIONS, NUMERIC_CONSTRAINTS, MAX_DESCRIPTION_LENGTH,
    COMMON_PARAM_NAMES, SPECIAL_PARAM_NAMES, classify_chart_param,
)
from dash_chart_editor.aio.pydantic_chart_editor import (
    _RELAYOUT_TO_LAYOUT, _PX_API_BASE, PydanticChartEditor,
    _build_charts_fields_repr, _EditorState,
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


def test_param_section_classification():
    """classify_chart_param should return correct section for known params."""
    # Common: core column selectors + opacity
    assert classify_chart_param("x") == "common"
    assert classify_chart_param("y") == "common"
    assert classify_chart_param("color") == "common"
    assert classify_chart_param("size") == "common"
    assert classify_chart_param("names") == "common"
    assert classify_chart_param("values") == "common"
    assert classify_chart_param("opacity") == "common"
    # Advanced: facets, animation, error bars, etc.
    assert classify_chart_param("facet_row") == "advanced"
    assert classify_chart_param("facet_col") == "advanced"
    assert classify_chart_param("animation_frame") == "advanced"
    # Special: trendlines, marginals, display modes, etc.
    assert classify_chart_param("trendline") == "special"
    assert classify_chart_param("barmode") == "special"
    assert classify_chart_param("orientation") == "special"
    assert classify_chart_param("marginal_x") == "special"
    assert classify_chart_param("log_x") == "special"


def test_common_and_special_param_sets_non_overlapping():
    """COMMON_PARAM_NAMES and SPECIAL_PARAM_NAMES must be disjoint."""
    overlap = COMMON_PARAM_NAMES & SPECIAL_PARAM_NAMES
    assert not overlap, f"Overlapping params: {overlap}"


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
    """_EditorState should combine a charts list (union of section-based models) with _LayoutConfig."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState, _LayoutConfig

    state = _EditorState.model_validate(
        {
            "charts": [
                {"name": "A", "chart_type": "scatter", "data_source": "ds",
                 "common": {"x": "x", "y": "y"}},
                {"name": "B", "chart_type": "bar", "data_source": "ds",
                 "common": {"x": "cat", "y": "val"}},
            ],
            "shared_layout": {"title": "Combined", "showlegend": True},
        }
    )
    assert len(state.charts) == 2
    assert state.charts[0].name == "A"
    assert state.charts[1].chart_type == "bar"
    assert state.shared_layout.title == "Combined"
    assert state.shared_layout.showlegend is True


def test_chart_entry_section_models():
    """Each chart entry should expose common/advanced/special section sub-models."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState

    state = _EditorState.model_validate(
        {
            "charts": [
                {"chart_type": "scatter", "data_source": "ds",
                 "common": {"x": "sepal_length", "y": "sepal_width", "color": "species"}},
            ],
            "shared_layout": {},
        }
    )
    entry = state.charts[0]
    assert hasattr(entry, "common")
    assert hasattr(entry, "advanced")
    assert hasattr(entry, "special")
    assert entry.common.x == "sepal_length"
    assert entry.common.y == "sepal_width"
    assert entry.common.color == "species"


def test_chart_entry_flat_input_reshaping():
    """Flat input dicts (backward compat) should be reshaped into section sub-models."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState

    state = _EditorState.model_validate(
        {
            "charts": [
                {"chart_type": "pie", "data_source": "ds", "names": "category", "values": "amount"},
            ],
            "shared_layout": {},
        }
    )
    entry = state.charts[0]
    # names and values are common params → should land in common section
    assert entry.common.names == "category"
    assert entry.common.values == "amount"
    # x/y are not valid kwargs for pie, so the common section should not have them
    assert "x" not in type(entry.common).model_fields


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
    """_EditorState should validate entries against union models via flat or section dicts."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState

    # Section-based input
    state = _EditorState.model_validate(
        {
            "charts": [
                {
                    "name": "S1",
                    "chart_type": "scatter",
                    "data_source": "Iris",
                    "common": {"x": "sepal_length", "y": "sepal_width"},
                },
                {
                    "name": "P1",
                    "chart_type": "pie",
                    "data_source": "Tips",
                    "common": {"names": "day", "values": "total_bill"},
                },
            ],
            "shared_layout": {"title": "Combined"},
        }
    )
    assert len(state.charts) == 2
    assert state.charts[0].chart_type == "scatter"
    assert state.charts[1].chart_type == "pie"
    assert state.shared_layout.title == "Combined"

    # Flat input (backward compat – should also be accepted via model_validator)
    state2 = _EditorState.model_validate(
        {
            "charts": [
                {
                    "name": "S2",
                    "chart_type": "scatter",
                    "data_source": "Iris",
                    "x": "sepal_length",
                    "y": "sepal_width",
                },
            ],
            "shared_layout": {},
        }
    )
    assert len(state2.charts) == 1
    assert state2.charts[0].common.x == "sepal_length"


def test_dynamic_editor_state_legacy_label_maps_to_name():
    """Legacy `label` should still be accepted and mapped to `name`."""
    from dash_chart_editor.aio.pydantic_chart_editor import _EditorState

    state = _EditorState.model_validate(
        {
            "charts": [
                {"label": "Legacy", "chart_type": "scatter", "data_source": "Iris"},
            ],
            "shared_layout": {},
        }
    )
    assert state.charts[0].name == "Legacy"


# ── Data transforms tests ─────────────────────────────────────────────────────

def test_data_filter_equality():
    """_apply_transforms: equality filter should remove non-matching rows."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _apply_transforms, _DataTransforms, _DataFilter

    df = pd.DataFrame({"species": ["setosa", "versicolor", "setosa"], "value": [1, 2, 3]})
    transforms = _DataTransforms(
        filters=[_DataFilter(column="species", operator="==", value="setosa")]
    )
    result = _apply_transforms(df, transforms)
    assert list(result["species"]) == ["setosa", "setosa"]
    assert len(result) == 2


def test_data_filter_numeric_cast():
    """_apply_transforms: filter value is auto-cast to numeric for numeric columns."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _apply_transforms, _DataTransforms, _DataFilter

    df = pd.DataFrame({"score": [10, 20, 30], "label": ["a", "b", "c"]})
    transforms = _DataTransforms(
        filters=[_DataFilter(column="score", operator=">", value="15")]
    )
    result = _apply_transforms(df, transforms)
    assert list(result["score"]) == [20, 30]


def test_data_groupby_aggregation():
    """_apply_transforms: group-by with sum aggregation should aggregate correctly."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import (
        _apply_transforms, _DataTransforms, _DataGroupBy,
    )

    df = pd.DataFrame({
        "category": ["A", "B", "A", "B"],
        "amount": [10, 20, 30, 40],
    })
    transforms = _DataTransforms(
        group_by=_DataGroupBy(group_by_columns=["category"], agg_columns=["amount"], agg_function="sum")
    )
    result = _apply_transforms(df, transforms)
    result = result.sort_values("category").reset_index(drop=True)
    assert list(result["amount"]) == [40, 60]  # A=10+30, B=20+40


def test_data_groupby_multi_columns_and_aggregates():
    """_apply_transforms: multi-column group-by and multi-column aggregate should work."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import (
        _apply_transforms, _DataTransforms, _DataGroupBy,
    )

    df = pd.DataFrame({
        "region": ["E", "E", "W", "W"],
        "segment": ["A", "A", "A", "B"],
        "sales": [10, 20, 30, 40],
        "profit": [1, 2, 3, 4],
    })
    transforms = _DataTransforms(
        group_by=_DataGroupBy(
            group_by_columns=["region", "segment"],
            agg_columns=["sales", "profit"],
            agg_function="sum",
        )
    )
    result = _apply_transforms(df, transforms).sort_values(["region", "segment"]).reset_index(drop=True)
    assert list(result["region"]) == ["E", "W", "W"]
    assert list(result["segment"]) == ["A", "A", "B"]
    assert list(result["sales"]) == [30, 30, 40]
    assert list(result["profit"]) == [3, 3, 4]


def test_data_groupby_legacy_keys_map_to_lists():
    """_DataGroupBy should map legacy singular keys to list fields."""
    from dash_chart_editor.aio.pydantic_chart_editor import _DataGroupBy

    gb = _DataGroupBy.model_validate({"group_by": "category", "agg_column": "amount"})
    assert gb.group_by_columns == ["category"]
    assert gb.agg_columns == ["amount"]
    assert gb.agg_function == "sum"


def test_data_groupby_legacy_keys_end_to_end():
    """Legacy group_by/agg_column keys should still work through _apply_transforms."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _apply_transforms, _DataTransforms

    df = pd.DataFrame({
        "category": ["A", "A", "B"],
        "amount": [5, 7, 3],
    })
    transforms = _DataTransforms.model_validate(
        {"group_by": {"group_by": "category", "agg_column": "amount", "agg_function": "sum"}}
    )
    result = _apply_transforms(df, transforms).sort_values("category").reset_index(drop=True)
    assert list(result["category"]) == ["A", "B"]
    assert list(result["amount"]) == [12, 3]


def test_data_sort():
    """_apply_transforms: sort descending should reverse the order."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _apply_transforms, _DataTransforms, _DataSort

    df = pd.DataFrame({"val": [3, 1, 2]})
    transforms = _DataTransforms(sort=_DataSort(sort_by="val", direction="desc"))
    result = _apply_transforms(df, transforms)
    assert list(result["val"]) == [3, 2, 1]


def test_transforms_skip_on_missing_column():
    """_apply_transforms: filter on a missing column should not raise and returns original df."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _apply_transforms, _DataTransforms, _DataFilter

    df = pd.DataFrame({"a": [1, 2, 3]})
    transforms = _DataTransforms(
        filters=[_DataFilter(column="nonexistent", operator="==", value="x")]
    )
    result = _apply_transforms(df, transforms)
    assert len(result) == 3  # unchanged


def test_transforms_field_in_dynamic_chart_model():
    """Dynamic chart models should include a 'transforms' field of type _DataTransforms."""
    from dash_chart_editor.aio.pydantic_chart_editor import _get_chart_union_models, _DataTransforms
    models = _get_chart_union_models()
    scatter_model = next(
        (m for m in models if getattr(m.model_fields.get("chart_type"), "default", None) == "scatter"),
        None,
    )
    assert scatter_model is not None, "Scatter model not found in union models"
    assert "transforms" in scatter_model.model_fields
    field_info = scatter_model.model_fields["transforms"]
    assert field_info.annotation is _DataTransforms or issubclass(field_info.annotation, _DataTransforms)


# ── Data source dropdown + column select fields_repr tests ───────────────────

def test_build_charts_fields_repr_data_source_is_select():
    """_build_charts_fields_repr: data_source override should be a Select field."""
    from dash_chart_editor.aio.pydantic_chart_editor import _build_charts_fields_repr
    from dash_pydantic_form import fields as pydf_fields

    repr_dict = _build_charts_fields_repr(["iris", "tips"], ["sepal_length", "sepal_width"])
    inner = repr_dict.get("fields_repr", {})
    ds_field = inner.get("data_source")
    assert ds_field is not None, "data_source field repr not found"
    assert isinstance(ds_field, pydf_fields.Select), f"Expected Select, got {type(ds_field)}"
    assert "iris" in ds_field.options_labels
    assert "tips" in ds_field.options_labels


def test_build_charts_fields_repr_common_x_y_are_selects():
    """Column kwargs in the common section should be overridden with Select."""
    from dash_chart_editor.aio.pydantic_chart_editor import _build_charts_fields_repr
    from dash_pydantic_form import fields as pydf_fields

    columns = ["col_a", "col_b", "col_c"]
    repr_dict = _build_charts_fields_repr(["src1"], columns)
    inner = repr_dict.get("fields_repr", {})
    common_repr = inner.get("common", {}).get("fields_repr", {})
    # x and y are common column kwargs
    assert "x" in common_repr, "x not in common fields_repr"
    assert "y" in common_repr, "y not in common fields_repr"
    assert isinstance(common_repr["x"], pydf_fields.Select)
    assert isinstance(common_repr["y"], pydf_fields.Select)
    assert "col_a" in common_repr["x"].options_labels


def test_build_charts_fields_repr_empty_sources_no_select():
    """No data sources → no fields_repr overrides (form reverts to plain inputs)."""
    from dash_chart_editor.aio.pydantic_chart_editor import _build_charts_fields_repr

    repr_dict = _build_charts_fields_repr([], [])
    # Should only have form_layout, no fields_repr
    assert "fields_repr" not in repr_dict


def test_pydantic_chart_editor_stores_all_columns():
    """PydanticChartEditor should compute all_columns as union of data source columns."""
    import pandas as pd
    from dash_chart_editor.aio.pydantic_chart_editor import _build_charts_fields_repr

    df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2 = pd.DataFrame({"b": [5, 6], "c": [7, 8]})
    all_columns = sorted(set(col for df in [df1, df2] for col in df.columns))
    repr_dict = _build_charts_fields_repr(["src1", "src2"], all_columns)
    inner = repr_dict.get("fields_repr", {})
    common_repr = inner.get("common", {}).get("fields_repr", {})
    # x and y Select options should include all columns (a, b, c)
    assert "x" in common_repr, "x not in common fields_repr"
    x_options = common_repr["x"].options_labels
    assert "a" in x_options, "column 'a' not in x Select options"
    assert "c" in x_options, "column 'c' not in x Select options"


# ── Dynamic callback logic tests ─────────────────────────────────────────────

def test_track_selected_sources_updates_on_change():
    """track_selected_sources logic: returns new list when sources change, no_update when same."""
    from dash import no_update

    def _track(form_data, prev_sources):
        """Mirror the callback logic without Dash context."""
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

    # Sources change → should return new list
    form_data = {"charts": [{"data_source": "iris"}, {"data_source": "tips"}]}
    result = _track(form_data, ["iris"])
    assert result == ["iris", "tips"]

    # Sources unchanged → no_update
    result = _track(form_data, ["iris", "tips"])
    assert result is no_update

    # Empty form_data → no_update
    result = _track({}, ["iris"])
    assert result is no_update

    # None form_data → no_update
    result = _track(None, None)
    assert result is no_update


def test_clean_form_data_removes_invalid_columns():
    """_clean_form_data_for_sources should clear column values not in the selected source."""
    col_names = {
        "iris": ["sepal_length", "sepal_width", "species"],
        "tips": ["total_bill", "tip", "sex"],
    }
    form_data = {
        "charts": [
            {
                "data_source": "iris",
                "common": {
                    "x": "sepal_length",   # valid for iris
                    "y": "total_bill",     # invalid for iris (belongs to tips)
                    "color": "species",    # valid for iris
                },
            },
            {
                "data_source": "tips",
                "common": {
                    "x": "total_bill",     # valid for tips
                    "y": "sepal_width",    # invalid for tips
                },
            },
        ]
    }
    cleaned = PydanticChartEditor._clean_form_data_for_sources(form_data, col_names)

    iris_common = cleaned["charts"][0]["common"]
    assert iris_common.get("x") == "sepal_length", "valid x should be kept"
    assert "y" not in iris_common, "invalid y (total_bill) should be dropped for iris"
    assert iris_common.get("color") == "species", "valid color should be kept"

    tips_common = cleaned["charts"][1]["common"]
    assert tips_common.get("x") == "total_bill", "valid x should be kept"
    assert "y" not in tips_common, "invalid y (sepal_width) should be dropped for tips"


def test_rebuild_form_changes_fields_repr_options():
    """rebuild_form_on_source_change should produce column options from selected sources only."""
    col_names = {
        "iris": ["sepal_length", "sepal_width", "species"],
        "tips": ["total_bill", "tip", "sex"],
    }

    # Simulate what rebuild_form_on_source_change does internally
    selected_sources = ["iris"]
    selected_cols = set()
    for src in selected_sources:
        if src and src in col_names:
            selected_cols.update(col_names[src])
    all_selected_cols = sorted(selected_cols)

    charts_fields_repr = _build_charts_fields_repr(list(col_names.keys()), all_selected_cols)
    inner = charts_fields_repr.get("fields_repr", {})
    common_repr = inner.get("common", {}).get("fields_repr", {})

    x_field = common_repr.get("x")
    assert x_field is not None, "x field repr should exist"
    x_options = x_field.options_labels

    # Only iris columns should be in the options (not tips columns)
    assert "sepal_length" in x_options
    assert "sepal_width" in x_options
    assert "total_bill" not in x_options, "tips column should not appear when only iris is selected"
    assert "tip" not in x_options, "tips column should not appear when only iris is selected"
