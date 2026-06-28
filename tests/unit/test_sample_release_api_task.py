from unittest.mock import MagicMock

import pytest

from src.sample_release_api_task import SetSystemMessage


@pytest.fixture
def task():
    """A SetSystemMessage task whose Release API client is mocked.

    SetSystemMessage builds its client through ``get_release_api_client()`` and
    calls ``.put()`` on it. Replacing that factory with a mock lets ``execute()``
    run offline while we assert what it sends.
    """
    t = SetSystemMessage()
    t.api_client = MagicMock()
    t.get_release_api_client = MagicMock(return_value=t.api_client)
    return t


def test_sets_system_message(task):
    # Given
    task.input_properties = {"task_id": "task_1", "message": "Deploy in progress"}

    # When
    task.execute()

    # Then -- the configured message is PUT to the system-message config endpoint
    task.api_client.put.assert_called_once()
    args, kwargs = task.api_client.put.call_args
    assert args[0] == "/api/v1/config/system-message"
    payload = kwargs["json"]
    assert payload["message"] == "Deploy in progress"
    assert payload["type"] == "xlrelease.SystemMessageSettings"
    assert payload["enabled"] == "True"


def test_rejects_empty_message(task):
    # Given
    task.input_properties = {"task_id": "task_1", "message": ""}

    # When / Then -- it fails before building a client or calling the API
    with pytest.raises(ValueError, match="cannot be empty"):
        task.execute()
    task.get_release_api_client.assert_not_called()
    task.api_client.put.assert_not_called()
