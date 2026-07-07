"""Shared fixtures for live integration tests.

These tests run against a real Digital.ai Release server and skip themselves
when none is reachable. Point them at a server with environment variables
(defaults shown):

    RELEASE_SERVER_URL   (default: http://localhost:5516)
    RELEASE_USERNAME     (default: admin)
    RELEASE_PASSWORD     (default: admin)
"""
import os

import pytest

from digitalai.release.release_api_client import ReleaseAPIClient
from com.xebialabs.xlrelease.api.v1.settings_api import SettingsApi

SERVER_URL = os.environ.get("RELEASE_SERVER_URL", "http://localhost:5516")
USERNAME = os.environ.get("RELEASE_USERNAME", "admin")
PASSWORD = os.environ.get("RELEASE_PASSWORD", "admin")


@pytest.fixture
def live_client():
    """A ReleaseAPIClient pointed at the configured server.

    Skips the test when the server cannot be reached, so the suite still passes
    on machines without a running Release instance.
    """
    client = ReleaseAPIClient(SERVER_URL, USERNAME, PASSWORD, timeout=10)
    try:
        SettingsApi(client).getInstanceInformation()
    except Exception as exc:
        pytest.skip(f"Release server not reachable at {SERVER_URL}: {exc}")
    return client
