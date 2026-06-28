"""End-to-end test for CreateAndStartRelease against a live Release server.

Unlike the mocked unit test, this drives the task against a real Digital.ai
Release instance and verifies the release is actually created and started.

The ``live_client`` fixture (see conftest.py) skips the test when no server is
reachable, so it is safe to run anywhere.
"""
import uuid

import pytest

from com.xebialabs.xlrelease.api.v1.release_api import ReleaseApi

from src.create_and_start_release import CreateAndStartRelease

pytestmark = pytest.mark.integration


def test_create_and_start_release_live(live_client):
    # Given -- a task wired to the live server, with a unique title per run
    release_title = f"IT Demo Release {uuid.uuid4().hex[:8]}"
    task = CreateAndStartRelease()
    task._api_client = live_client  # seeds ApiBaseTask.apiClient; wrappers reuse it
    task.input_properties = {
        "task_id": "task_1",
        "releaseTitle": release_title,
        "phaseTitle": "Run Release Automation",
        "taskTitle": "Run legacy Jython script",
    }

    release_api = ReleaseApi(live_client)
    release_id = None
    try:
        # When
        task.execute_task()

        # Then -- the task finished cleanly and reported the started release
        assert task.get_output_context().exit_code == 0, \
            task.get_output_context().job_error_message
        outputs = task.get_output_properties()
        release_id = outputs["releaseId"]
        assert release_id
        assert outputs["releaseStatus"] == "IN_PROGRESS"

        # ...and the server confirms the release independently
        release = release_api.getRelease(release_id)
        assert release.title == release_title
        assert release.status == "IN_PROGRESS"

        phase = release.phases[0]
        assert phase.title == "Run Release Automation"
        jython_task = phase.tasks[0]
        assert jython_task.title == "Run legacy Jython script"
        assert jython_task.type == "xlrelease.ScriptTask"
    finally:
        # Clean up so repeated runs do not pile up releases on the server.
        if release_id:
            try:
                release_api.delete(release_id)
            except Exception:
                pass
