from datetime import datetime, timedelta, timezone

from com.xebialabs.xlrelease.api.v1.api_base_task import ApiBaseTask
from com.xebialabs.xlrelease.domain.forms import CreateRelease
from com.xebialabs.xlrelease.domain.release import Release
from com.xebialabs.xlrelease.domain.task import Task


class CreateAndStartRelease(ApiBaseTask):
    """Create a release, add a phase and a Jython task, start it, and print the result."""

    def execute(self) -> None:

        # Read input properties, falling back to defaults.
        release_title = self.input_properties.get("releaseTitle") or "Demo Release 1.0.0"
        phase_title = self.input_properties.get("phaseTitle") or "Run Release Automation"
        task_title = self.input_properties.get("taskTitle") or "Run Jython script"

        # The API wrappers (self.templateApi, self.releaseApi, self.phaseApi,
        # self.taskApi) are provided by ApiBaseTask. They are created lazily and
        # share a single client built from the task's "Run as user" context.

        # 1. Create a template (releases are always created from one); the server requires a start date.
        start = datetime.now(timezone.utc)
        template = self.templateApi.createTemplate(
            Release(
                title=f"{release_title} - Template",
                scheduledStartDate=start,
                dueDate=start + timedelta(days=7),
            )
        )
        print(f"[1] Template created -> id={template.id}, title='{template.title}'")

        # Create the release from the template; it starts in PLANNED state, ready to edit.
        release = self.templateApi.create(
            template.id,
            CreateRelease(releaseTitle=release_title),
        )
        print(
            f"[1] Release created  -> id={release.id}, "
            f"title='{release.title}', status={release.status}"
        )

        # 2. Templates come with a default empty phase; reuse it by renaming it.
        created = self.releaseApi.getRelease(release.id)
        phase = created.phases[0]
        phase.title = phase_title
        phase = self.phaseApi.updatePhase(phase.id, phase)
        print(f"[2] Phase renamed    -> id={phase.id}, title='{phase.title}'")

        # 3. Add a Jython script task ("xlrelease.ScriptTask" runs Jython via the "script" property).
        jython_script = (
            "print 'Hello from the Jython script task!'\n"
            "print 'This task was created via the release_api_client.'\n"
            "print 'Release automation is running...'\n"
        )
        task = self.taskApi.addTask(
            phase.id,
            Task(title=task_title, type="xlrelease.ScriptTask", script=jython_script),
        )
        print(
            f"[3] Jython task added -> id={task.id}, "
            f"title='{task.title}', type={task.type}"
        )

        # 4. Start the release (PLANNED -> IN_PROGRESS).
        started = self.releaseApi.start(release.id)
        print(f"[4] Release started  -> id={started.id}, status={started.status}")

        # 5. Re-fetch and print a summary of the running release.
        summary = self.releaseApi.getRelease(started.id)
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
