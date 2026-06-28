"""End-to-end test for SetSystemMessage against a live Release server.

This mutates instance-wide configuration (the system message banner), so it
saves the current settings first and restores them afterwards.

The ``live_client`` fixture (see conftest.py) skips the test when no server is
reachable, so it is safe to run anywhere.
"""
import uuid

import pytest

from src.sample_release_api_task import SetSystemMessage

pytestmark = pytest.mark.integration

ENDPOINT = "/api/v1/config/system-message"


def test_set_system_message_live(live_client):
    # Save current settings so the instance config can be restored afterwards.
    original = live_client.get(ENDPOINT).json()

    message = f"Integration test message {uuid.uuid4().hex[:8]}"
    task = SetSystemMessage()
    # Make the task use the live client instead of building one from task context.
    task.get_release_api_client = lambda *args, **kwargs: live_client
    task.input_properties = {"task_id": "task_1", "message": message}

    try:
        # When
        task.execute()

        # Then -- the server reflects the new system message
        current = live_client.get(ENDPOINT).json()
        assert current["message"] == message
        assert current["enabled"] in (True, "True")
    finally:
        # Restore the original system-message configuration.
        live_client.put(ENDPOINT, json=original)
