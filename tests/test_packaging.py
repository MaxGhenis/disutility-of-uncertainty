"""The installed distribution must carry its published result resources."""

import json
from importlib.resources import files


def test_published_data_resources_are_readable():
    resources = files("taxuncertainty.data")
    assert isinstance(json.loads(resources.joinpath("results.json").read_text()), dict)
    assert resources.joinpath("parameters.yaml").read_text().strip()


def test_national_estimate_resource_validates():
    from taxuncertainty.analysis.national import load_national_estimate

    resource = files("taxuncertainty.data").joinpath("national_estimate.json")
    assert load_national_estimate(resource)["schema_version"] == 1
