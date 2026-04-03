"""Shared fixtures for eval tests."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def eval_config():
    config_path = Path(__file__).parent / "eval_config.json"
    with open(config_path) as f:
        return json.load(f)


@pytest.fixture
def test_cases(eval_config):
    return eval_config["test_cases"]
