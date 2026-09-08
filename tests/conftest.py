"""Keep live PolicyEngine validation separate from the fast test suite."""

import importlib.util

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-policyengine",
        action="store_true",
        default=False,
        help="Run optional live PolicyEngine validation; requires .[policyengine].",
    )


def pytest_collection_modifyitems(config, items):
    requested = config.getoption("--run-policyengine")
    available = importlib.util.find_spec("policyengine") is not None
    for item in items:
        if "policyengine" not in item.keywords and "slow" not in item.keywords:
            continue
        if not requested:
            item.add_marker(
                pytest.mark.skip(
                    reason="Enable live validation with --run-policyengine"
                )
            )
        elif not available:
            raise pytest.UsageError(
                "--run-policyengine requires the optional dependency: "
                "uv sync --extra dev --extra policyengine --locked"
            )
