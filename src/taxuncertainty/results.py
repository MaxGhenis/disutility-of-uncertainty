"""Results accessor with dot-notation and formatted strings.

Provides convenient attribute access to the results JSON for use
in paper templates and analysis notebooks.
"""

import json
from pathlib import Path


def _wrap(value):
    """Recursively wrap dicts as _DotDict and lists of dicts as lists of _DotDict."""
    if isinstance(value, dict):
        return _DotDict(value)
    if isinstance(value, list):
        return [_wrap(item) for item in value]
    return value


class _DotDict:
    """Dict with attribute access and _fmt suffixed formatted strings."""

    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, _wrap(v))
            if isinstance(v, float):
                setattr(self, f"{k}_fmt", f"{v:.2f}")
            elif isinstance(v, int):
                setattr(self, f"{k}_fmt", f"{v:,}")


class Results:
    """Load versioned paper results with dot notation.

    Version 2 distinguishes private regret, fiscal changes, and social losses.
    The former national DWL fields are intentionally absent.

    Parameters
    ----------
    path : str or Path or None
        Path to results.json. If None, uses the default location
        in the package data directory.

    Examples
    --------
    >>> r = Results("results.json")
    >>> r.schema_version
    2
    >>> r.scenarios[1].worker.private_regret_fmt
    '190.11'
    """

    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).parent / "data" / "results.json"
        with open(path) as f:
            data = json.load(f)
        for k, v in data.items():
            setattr(self, k, _wrap(v))
