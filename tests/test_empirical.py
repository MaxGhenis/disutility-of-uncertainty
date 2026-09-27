"""Legacy clipped-rate population estimates cannot silently regenerate."""

import pytest

from taxuncertainty.analysis.empirical import (
    EmpiricalMTR,
    UnsupportedEmpiricalEstimateError,
)


@pytest.mark.parametrize(
    "kwargs", [{}, {"year": 2024, "cache": True}, {"year": 2026, "cache": False}]
)
def test_legacy_empirical_path_fails_with_methodology_error(kwargs):
    with pytest.raises(UnsupportedEmpiricalEstimateError, match="retired.*provenance"):
        EmpiricalMTR(**kwargs)
