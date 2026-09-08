"""The installed distribution must carry its published result resources."""

import json
from importlib.resources import files


def test_published_data_resources_are_readable():
    resources = files("taxuncertainty.data")
    assert isinstance(json.loads(resources.joinpath("results.json").read_text()), dict)
    assert resources.joinpath("parameters.yaml").read_text().strip()
