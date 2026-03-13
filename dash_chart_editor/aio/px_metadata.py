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
    """Return a mapping of param name -> list of valid string options based on _doc.docs."""
    fixed: dict[str, list[str]] = {}
    for param, docs in _doc.docs.items():
        combined = " ".join(docs if isinstance(docs, list) else [docs])
        if "one of" in combined.lower():
            options = list(dict.fromkeys(_OPTION_PATTERN.findall(combined)))
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

        for param in sig.parameters.values():
            if param.name == "data_frame":
                continue
            if param.kind not in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
                continue

            kwargs.append(param.name)
            arg_types[param.name] = _infer_param_type(param)

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
        }

    return metadata


PX_CHART_METADATA = get_px_chart_metadata()
