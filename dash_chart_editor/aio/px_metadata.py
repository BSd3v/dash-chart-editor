"""Utilities for parsing Plotly Express chart kwargs metadata."""

from __future__ import annotations

import re
from inspect import Parameter, getmembers, isfunction, signature
from typing import Any

from plotly.express import _chart_types, _doc

# Internal helpers that should not appear as chart type options
_INTERNAL_NAMES: frozenset[str] = frozenset({"make_figure", "make_docstring"})

_COLUMN_PHRASES = (
    "either a name of a column in `data_frame`",
    _doc.colref_desc.lower(),
)

_MULTI_COLUMN_PHRASES = (
    "either a list of names of columns in `data_frame`",
    "either names of columns in `data_frame`",
    "can optionally be a list of column references",
    _doc.colref_list_desc.lower(),
)

_OPTION_PATTERN = re.compile(r"[`'\"]([a-z_]+)[`'\"]")

# Collect every parameter name used across all px chart functions.
# Used to filter out false-positive option values that are actually param references.
_ALL_PX_PARAM_NAMES: frozenset[str] = frozenset(
    pname
    for _, fn in getmembers(_chart_types, isfunction)
    for pname in signature(fn).parameters
)

# Well-known numeric parameters with their type and optional ge/le constraints.
# These override the inferred type (which often falls back to str) and are used
# to generate number inputs with appropriate min/max bounds in the form.
NUMERIC_CONSTRAINTS: dict[str, dict[str, Any]] = {
    "opacity": {"type": float, "ge": 0.0, "le": 1.0},
    "facet_col_wrap": {"type": int, "ge": 0},
    "facet_row_spacing": {"type": float, "ge": 0.0, "le": 1.0},
    "facet_col_spacing": {"type": float, "ge": 0.0, "le": 1.0},
    "size_max": {"type": int, "ge": 1},
    "nbins": {"type": int, "ge": 0},
    "nbinsx": {"type": int, "ge": 0},
    "nbinsy": {"type": int, "ge": 0},
    "color_continuous_midpoint": {"type": float},
    "maxdepth": {"type": int, "ge": -1},
    "start_angle": {"type": int, "ge": 0, "le": 360},
    "zoom": {"type": int, "ge": 0, "le": 20},
    "width": {"type": int, "ge": 100},   # minimum 100px to keep chart usable
    "height": {"type": int, "ge": 100},  # minimum 100px to keep chart usable
    "hole": {"type": float, "ge": 0.0, "le": 1.0},
}


def _iter_chart_functions():
    return [
        (name, fn)
        for name, fn in getmembers(_chart_types, isfunction)
        if name not in _INTERNAL_NAMES
    ]


def _parse_param_docs(docstring: str) -> dict[str, str]:
    docs: dict[str, list[str]] = {}
    current: str | None = None

    for raw_line in (docstring or "").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        if ":" in stripped and not stripped.startswith(("-", "*")):
            candidate = stripped.split(":", 1)[0].strip()
            if candidate and " " not in candidate and candidate.replace("_", "").isalnum():
                current = candidate
                docs.setdefault(current, [])
                continue

        if current:
            docs[current].append(stripped)

    return {key: " ".join(value).lower() for key, value in docs.items()}


def _infer_param_type(param: Parameter) -> type[Any]:
    if param.annotation is not Parameter.empty and isinstance(param.annotation, type):
        return param.annotation

    if param.default is not Parameter.empty and param.default is not None:
        return type(param.default)

    return str


def _get_fixed_options() -> dict[str, list[str]]:
    """Return a mapping of param name -> list of valid string options based on _doc.docs.

    Options that are themselves px parameter names are excluded to prevent false positives
    (e.g. the orientation docs mention `x` and `y` as column references, not valid values).
    """
    fixed: dict[str, list[str]] = {}
    for param, docs in _doc.docs.items():
        combined = " ".join(docs if isinstance(docs, list) else [docs])
        if "one of" in combined.lower():
            options = [
                opt
                for opt in dict.fromkeys(_OPTION_PATTERN.findall(combined))
                # Exclude options that are actually px parameter names (false positives from
                # references to other params in the documentation text)
                if opt not in _ALL_PX_PARAM_NAMES
            ]
            if options:
                fixed[param] = options
    return fixed


# Global mapping: param name -> list of allowed string values (for dropdown rendering)
FIXED_OPTIONS: dict[str, list[str]] = _get_fixed_options()


def get_px_chart_metadata() -> dict[str, dict[str, Any]]:
    """Return metadata for each Plotly Express chart function.

    The metadata includes supported kwargs and which kwargs accept column refs,
    based on the doc parsing strategy used in Dashboard-Helper.
    """

    metadata: dict[str, dict[str, Any]] = {}

    for chart_name, chart_fn in _iter_chart_functions():
        sig = signature(chart_fn)
        param_docs = _parse_param_docs(chart_fn.__doc__ or "")

        kwargs: list[str] = []
        column_kwargs: list[str] = []
        multi_column_kwargs: list[str] = []
        arg_types: dict[str, type[Any]] = {}
        fixed_options: dict[str, list[str]] = {}
        param_defaults: dict[str, Any] = {}

        for param in sig.parameters.values():
            if param.name == "data_frame":
                continue
            if param.kind not in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
                continue

            kwargs.append(param.name)
            arg_types[param.name] = _infer_param_type(param)

            # Store the signature default so the form can pre-select it
            if param.default is not Parameter.empty:
                param_defaults[param.name] = param.default

            # Record fixed options (finite enum-like choices) for this param
            if param.name in FIXED_OPTIONS:
                fixed_options[param.name] = FIXED_OPTIONS[param.name]

            details = param_docs.get(param.name, "")
            if param.name in {"x", "y"} and any(phrase in details for phrase in _MULTI_COLUMN_PHRASES):
                # Keep x/y as single-column selectors by default.
                # Plotly docs mention optional wide-form list support, but single selection
                # is the expected editor behavior.
                column_kwargs.append(param.name)
            elif any(phrase in details for phrase in _MULTI_COLUMN_PHRASES):
                multi_column_kwargs.append(param.name)
            elif any(phrase in details for phrase in _COLUMN_PHRASES):
                column_kwargs.append(param.name)

        metadata[chart_name] = {
            "kwargs": kwargs,
            "column_kwargs": column_kwargs,
            "multi_column_kwargs": multi_column_kwargs,
            "arg_types": arg_types,
            "fixed_options": fixed_options,
            "param_defaults": param_defaults,
        }

    return metadata


PX_CHART_METADATA = get_px_chart_metadata()
