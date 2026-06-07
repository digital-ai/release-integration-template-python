from datetime import datetime, timedelta, timezone

from digitalai.release.integration import BaseTask

from com.xebialabs.xlrelease.api.v1.phase_api import PhaseApi
from com.xebialabs.xlrelease.api.v1.release_api import ReleaseApi
from com.xebialabs.xlrelease.api.v1.task_api import TaskApi
from com.xebialabs.xlrelease.api.v1.template_api import TemplateApi
from com.xebialabs.xlrelease.domain.forms import CreateRelease
from com.xebialabs.xlrelease.domain.phase import Phase
from com.xebialabs.xlrelease.domain.release import Release
from com.xebialabs.xlrelease.domain.task import Task


class CreateAndStartRelease(BaseTask):
    """Create a release, add a phase and a Jython task, start it, and print the result."""

    def execute(self) -> None:

        # Read input properties, falling back to defaults.
        release_title = self.input_properties.get("releaseTitle") or "Demo Release 1.0.0"
        phase_title = self.input_properties.get("phaseTitle") or "Deploy"
        task_title = self.input_properties.get("taskTitle") or "Run Jython script"

        # API client (built from the task's "Run as user" context) and helpers.
        client = self.get_release_api_client()
        template_api = TemplateApi(client)
        release_api = ReleaseApi(client)
        phase_api = PhaseApi(client)
        task_api = TaskApi(client)

        # 1. Create a template (releases are always created from one); the server requires a start date.
        start = datetime.now(timezone.utc)
        template = template_api.createTemplate(
            Release(
                title=f"{release_title} - Template",
                scheduledStartDate=start,
                dueDate=start + timedelta(days=7),
            )
        )
        print(f"[1] Template created -> id={template.id}, title='{template.title}'")

        # Create the release from the template; it starts in PLANNED state, ready to edit.
        release = template_api.create(
            template.id,
            CreateRelease(releaseTitle=release_title),
        )
        print(
            f"[1] Release created  -> id={release.id}, "
            f"title='{release.title}', status={release.status}"
        )

        # 2. Templates come with a default empty phase; delete it so we end up with one phase.
        created = release_api.getRelease(release.id)
        for existing_phase in created.phases or []:
            phase_api.deletePhase(existing_phase.id)

        phase = phase_api.addPhase(release.id, Phase(title=phase_title))
        print(f"[2] Phase added      -> id={phase.id}, title='{phase.title}'")

        # 3. Add a Jython script task ("xlrelease.ScriptTask" runs Jython via the "script" property).
        jython_script = (
            "print 'Hello from the Jython script task!'\n"
            "print 'This task was created via the release_api_client.'\n"
            "print 'Release automation is running...'\n"
        )
        task = task_api.addTask(
            phase.id,
            Task(title=task_title, type="xlrelease.ScriptTask", script=jython_script),
        )
        print(
            f"[3] Jython task added -> id={task.id}, "
            f"title='{task.title}', type={task.type}"
        )

        # 4. Start the release (PLANNED -> IN_PROGRESS).
        started = release_api.start(release.id)
        print(f"[4] Release started  -> id={started.id}, status={started.status}")

        # 5. Re-fetch and print a summary of the running release.
        summary = release_api.getRelease(started.id)
        print("----- Release summary -----")
        print(f"  Title      : {summary.title}")
        print(f"  Id         : {summary.id}")
        print(f"  Status     : {summary.status}")
        print(f"  Start date : {summary.startDate}")
        for p in summary.phases or []:
            print(f"  Phase: '{p.title}' (status={p.status})")
            for t in p.tasks or []:
                print(f"      Task: '{t.title}' (status={t.status})")

        # Add a UI comment and expose results as output properties.
        self.add_comment(f"Created and started release '{summary.title}' ({summary.id})")
        self.set_output_property("releaseId", summary.id)
        self.set_output_property("releaseStatus", summary.status)
