from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client():
    """Provide a fresh app state for each test."""
    baseline = deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(deepcopy(baseline))

    with TestClient(app_module.app) as test_client:
        yield test_client

    app_module.activities.clear()
    app_module.activities.update(deepcopy(baseline))
