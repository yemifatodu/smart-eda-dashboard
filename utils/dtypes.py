"""
Robust dtype-detection helpers.

WHY THIS EXISTS: pandas 3.0 changed the default dtype for string columns
from the classic 'object' dtype to a new StringDtype. Code throughout this
project that checked `series.dtype == 'object'` or `.dtype.name == 'category'`
silently stopped detecting text columns — most visibly, the Auto-ML target
column would no longer get label-encoded, causing XGBoost to crash with
"Invalid classes inferred from unique values of `y`" on any string target
like Gender (Male/Female).

Use is_categorical_series() / is_categorical_column() everywhere instead of
hand-rolled dtype comparisons, so this keeps working across pandas versions.
"""

import pandas as pd


def is_categorical_series(series: pd.Series) -> bool:
    """True for text/categorical columns, regardless of pandas version's
    preferred string dtype (legacy object, new StringDtype, or category)."""
    return (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
        or isinstance(series.dtype, pd.CategoricalDtype)
    )


def categorical_columns(df: pd.DataFrame) -> list:
    """List of column names that are text/categorical, version-safe."""
    return [col for col in df.columns if is_categorical_series(df[col])]


def numeric_columns(df: pd.DataFrame) -> list:
    """Return column names holding numeric data."""
    return df.select_dtypes(include=['number']).columns.tolist()


def is_identifier_column(name: str, series: pd.Series = None) -> bool:
    """
    Heuristic for 'this numeric column is an ID, not a measurement'.
    Sequential IDs (Customer ID, Order ID, etc.) have huge variance and a
    unique value per row purely because they're counters - picking them as
    the 'most important' or 'highest value' metric produces meaningless
    insights like 'investigate why your highest Customer ID is so high'.
    """
    name_lower = name.lower().replace('_', ' ')
    if name_lower == 'id' or name_lower.endswith(' id') or name_lower.startswith('id '):
        return True
    if any(term in name_lower for term in ['identifier', 'uuid', 'index', 'row number']):
        return True
    if series is not None and len(series) > 0 and pd.api.types.is_integer_dtype(series):
        # Looks like a near-unique sequential counter. Restricted to integer
        # dtypes only - continuous float measurements (price, rating) are
        # also often near-unique and would otherwise be false-flagged here.
        if series.nunique() / len(series) > 0.98:
            return True
    return False


def meaningful_numeric_columns(df: pd.DataFrame) -> list:
    """Numeric columns with ID-like columns filtered out - use this instead
    of raw numeric_columns() when picking a 'primary metric' for narrative
    insights, so the story leads with something a business owner actually
    cares about instead of a row identifier."""
    numeric = numeric_columns(df)
    filtered = [c for c in numeric if not is_identifier_column(c, df[c])]
    # If everything got filtered out (e.g. a dataset that's all IDs), fall
    # back to the original list rather than returning nothing.
    return filtered if filtered else numeric
