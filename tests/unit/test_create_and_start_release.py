from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from com.xebialabs.xlrelease.api.v1.phase_api import PhaseApi
from com.xebialabs.xlrelease.api.v1.release_api import ReleaseApi
from com.xebialabs.xlrelease.api.v1.task_api import TaskApi
from com.xebialabs.xlrelease.api.v1.template_api import TemplateApi

from src.create_and_start_release import CreateAndStartRelease


@pytest.fixture
def task():
    """A CreateAndStartRelease task with its Release API wrappers mocked.

    ApiBaseTask caches API instances in ``_api_instances`` keyed by class, and
    only builds the real (network-backed) client when a wrapper is first
    accessed. Pre-seeding the cache with mocks means ``execute()`` runs fully
    offline -- the real client is never created.
    """
    t = CreateAndStartRelease()
    t._api_instances = {
        TemplateApi: MagicMock(),
        ReleaseApi: MagicMock(),
        PhaseApi: MagicMock(),
        TaskApi: MagicMock(),
    }
    return t


def test_creates_phase_task_and_starts_release(task):
    # Given -- a canned response for each step of execute()
    template = SimpleNamespace(id="Applications/tmpl1", title="Demo Release 1.0.0 - Template")
    release = SimpleNamespace(id="Applications/Release1", title="Demo Release 1.0.0", status="PLANNED")
    default_phase = SimpleNamespace(id="Applications/Release1/Phase1", title="New Phase")
    created = SimpleNamespace(phases=[default_phase])
    renamed_phase = SimpleNamespace(id=default_phase.id, title="Run Release Automation")
    added_task = SimpleNamespace(
        id="Applications/Release1/Phase1/Task1",
        title="Run Jython script",
        type="xlrelease.ScriptTask",
    )
    started = SimpleNamespace(id=release.id, status="IN_PROGRESS")
    summary = SimpleNamespace(
        id=release.id,
        title=release.title,
        status="IN_PROGRESS",
        startDate="2026-06-28T10:00:00+00:00",
        phases=[SimpleNamespace(
            title="Run Release Automation",
            status="IN_PROGRESS",
            tasks=[SimpleNamespace(title="Run Jython script", status="PLANNED")],
        )],
    )

    task.templateApi.createTemplate.return_value = template
    task.templateApi.create.return_value = release
    # getRelease is called twice: once to read the default phase, once for the summary.
    task.releaseApi.getRelease.side_effect = [created, summary]
    task.phaseApi.updatePhase.return_value = renamed_phase
    task.taskApi.addTask.return_value = added_task
    task.releaseApi.start.return_value = started

    task.input_properties = {
        "task_id": "task_1",
        "releaseTitle": "Demo Release 1.0.0",
        "phaseTitle": "Run Release Automation",
        "taskTitle": "Run Jython script",
    }

    # When
    task.execute_task()

    # Then -- the task finished cleanly (execute_task swallows exceptions into the exit code)
    assert task.get_output_context().exit_code == 0

    # ...and exposed the started release as output properties
    outputs = task.get_output_properties()
    assert outputs["releaseId"] == release.id
    assert outputs["releaseStatus"] == "IN_PROGRESS"

    # ...and drove the APIs in the expected shape
    task.templateApi.createTemplate.assert_called_once()
    task.templateApi.create.assert_called_once()
    assert task.releaseApi.getRelease.call_count == 2
    task.taskApi.addTask.assert_called_once()
    task.releaseApi.start.assert_called_once_with(release.id)

    # the default phase was renamed to the requested title before being saved
    saved_phase = task.phaseApi.updatePhase.call_args.args[1]
    assert saved_phase.title == "Run Release Automation"

    # the task that was added is a Jython script task
    new_task = task.taskApi.addTask.call_args.args[1]
    assert new_task.type == "xlrelease.ScriptTask"
    assert "Hello from the Jython script task!" in new_task.script
