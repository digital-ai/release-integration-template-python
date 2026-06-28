# Plugin Development Guide

A practical guide to building Digital.ai Release **container plugins** with this template.
It explains how the pieces fit together, how to add your own task, and how each
bundled example was built.

> New here? Read [How a container plugin works](#how-a-container-plugin-works) first,
> then jump to [Add a new task — step by step](#add-a-new-task--step-by-step).

## Contents

- [How a container plugin works](#how-a-container-plugin-works)
- [The two building blocks](#the-two-building-blocks)
- [The naming contract: type ↔ class](#the-naming-contract-type--class)
- [Anatomy of a task](#anatomy-of-a-task)
- [Choosing a base class: `BaseTask` vs `ApiBaseTask`](#choosing-a-base-class-basetask-vs-apibasetask)
- [Property kinds reference](#property-kinds-reference)
- [Add a new task — step by step](#add-a-new-task--step-by-step)
- [The example tasks explained](#the-example-tasks-explained)
- [Testing your task](#testing-your-task)
- [Build, install, run](#build-install-run)

---

## How a container plugin works

A container plugin contributes new **task types** to Release. When a user runs one of
your tasks, Release does roughly this:

```
 Release UI                Release server                 Container (your image)
┌──────────┐   run task   ┌───────────────┐  start pod  ┌──────────────────────┐
│  Task in │ ───────────► │ Reads the type │ ──────────► │ wrapper picks your   │
│ template │              │ definition,    │             │ Python class by name,│
│          │ ◄─────────── │ schedules the  │ ◄────────── │ runs execute(),      │
└──────────┘  outputs +   │ container image│  outputs    │ returns outputs      │
              comments     └───────────────┘             └──────────────────────┘
```

1. **Type definition** ([`resources/type-definitions.yaml`](resources/type-definitions.yaml))
   tells Release the task exists, what inputs/outputs it has, and which container image to run.
2. **Build** (`build.sh` / `build.bat`) produces two artifacts: a **plugin zip** (the type
   definitions + icons) installed into Release, and a **Docker image** (your `src/` code)
   pushed to a registry.
3. **At run time**, Release starts the image as a container. The entrypoint
   (`python -m digitalai.release.integration.wrapper`, see the [`Dockerfile`](Dockerfile))
   receives the task's input properties, finds the matching Python class, calls its
   `execute()` method, and sends the output properties and comments back to Release.

You write two things: the **type definition** (YAML) and the **task class** (Python).
The SDK wrapper handles everything in between.

---

## The two building blocks

### 1. The type definition (`resources/type-definitions.yaml`)

Declares the task to Release. Minimal example:

```yaml
types:
  containerExamples.Hello:
    extends: containerExamples.BaseTask     # inherits the image location + styling
    description: "Simple greeter task"

    input-properties:
      yourName:
        description: The name to greet
        kind: string
        default: World

    output-properties:
      greeting:
        kind: string
```

All tasks in this project extend `containerExamples.BaseTask`, a `virtual` (abstract)
type that sets the container image once for every task:

```yaml
  containerExamples.BaseTask:
    extends: xlrelease.ContainerTask
    virtual: true
    hidden-properties:
      image:
        default: "@registry.url@/@registry.org@/@project.name@:@project.version@"
        transient: true
      iconLocation: test.png
      taskColor: "#667385"
```

The `@...@` placeholders are filled in from [`project.properties`](project.properties) by
the build script, so the image tag always matches what you just built.

### 2. The task class (`src/`)

A Python class that does the work:

```python
from digitalai.release.integration import BaseTask


class Hello(BaseTask):

    def execute(self) -> None:
        name = self.input_properties['yourName']
        if not name:
            raise ValueError("The 'yourName' field cannot be empty")

        greeting = f"Hello {name}"
        self.add_comment(greeting)                 # shows in the task's UI comments
        self.set_output_property('greeting', greeting)
```

---

## The naming contract: type ↔ class

This is the one rule you must get right. Release sends the **task type** (e.g.
`containerExamples.Hello`) to the container, and the wrapper resolves it like this:

1. Split the type on the dot and take the part **after** it → `Hello`.
2. Search the image for a `.py` file that defines a class named exactly `Hello`.
3. Import that module and instantiate the class.

```
  type-definitions.yaml          src/hello.py
  containerExamples.Hello   ⇄    class Hello(BaseTask)
                    └── must match the class name exactly ──┘
```

Consequences:

- **The class name after the dot must match exactly** (case-sensitive).
- **The file name does not matter** — `Hello` could live in `src/anything.py`. By
  convention we name the file after the task, but the wrapper resolves by class name.
- **Keep class names unique** across `src/`, since resolution is by class name.

---

## Anatomy of a task

Every task subclasses `BaseTask` and implements **`execute(self) -> None`**. Inside it you
have these helpers (from `digitalai.release.integration.BaseTask`):

| Member | Purpose |
|--------|---------|
| `self.input_properties` | `dict` of the task's input properties, keyed by the names in `input-properties`. |
| `self.set_output_property(name, value)` | Set an output property (must be declared in `output-properties`). Allowed value types: `str`, `int`, `list`, `dict`, `bool`. |
| `self.get_output_properties()` | The current output properties `dict`. |
| `self.add_comment(text)` | Add a line to the task's **Comments** section in the UI. |
| `self.set_status_line(text)` | Set the task's status line. |
| `self.get_release_api_client(...)` | Build a `ReleaseAPIClient` to call the Release REST API (see below). |
| `raise ...` | Raising any exception fails the task; the message is shown to the user. |

**Lifecycle:** Release calls `execute_task()`, which sets up the output context and calls
your `execute()`. If `execute()` raises, the task is marked failed and the exception
message becomes the error message — you do **not** need to catch-and-report yourself.

---

## Choosing a base class: `BaseTask` vs `ApiBaseTask`

| | `BaseTask` | `ApiBaseTask` |
|--|------------|---------------|
| Import | `from digitalai.release.integration import BaseTask` | `from digitalai.release.integration.api_base_task import ApiBaseTask` |
| Use when | The task talks to a third-party system, or needs no Release API. | The task calls the **Release** REST API. |
| Release API access | Manual: `client = self.get_release_api_client()` | Ready-made: `self.releaseApi`, `self.phaseApi`, `self.taskApi`, `self.templateApi`, … |

`ApiBaseTask` exposes **every** Release v1 API as a lazily created, cached property. All of
them share a single client built from the task's **"Run as user"** context, so you just call:

```python
from digitalai.release.integration.api_base_task import ApiBaseTask


class ShowTitle(ApiBaseTask):
    def execute(self) -> None:
        release = self.releaseApi.getRelease(self.get_release_id())
        self.add_comment(f"Working on {release.title}")
```

> **"Run as user" matters.** API calls execute as the release's Run-as user. If that user
> is not set or lacks permission, API calls fail. For local testing, the dev-environment
> server (`localhost:5516`, `admin`/`admin`) has a working runner.

---

## Property kinds reference

The common `kind` values used in `input-properties` / `output-properties`:

| `kind` | Python type you receive | Notes |
|--------|-------------------------|-------|
| `string` | `str` | Plain text. Add `default:` for a default value. |
| `integer` | `int` | |
| `boolean` | `bool` | |
| `map_string_string` | `dict[str, str]` | Key/value pairs. |
| `ci` | `dict` | A reference to a configuration item; use `referenced-type:` to constrain it (e.g. a server connection). |

Other useful field options:

- `description:` — shown as help text in the UI.
- `default:` — pre-filled value.
- `required: true` — the UI enforces a value.
- `hidden-properties:` — properties not shown to the user (e.g. the container `image`).
- `input-hint: { method-ref: ... }` — drives a dropdown from a **lookup** script (see
  `HelloWithLookup` below).

A **server connection** is just a CI type that extends a Release connection type, so users
can pick a saved connection:

```yaml
  containerExamples.Server:
    extends: configuration.BasicAuthHttpConnection
    properties:
      url:
        default: https://dummyjson.com
        required: true
```

---

## Add a new task — step by step

Suppose you want a task that reverses a string.

**1. Declare the type** in [`resources/type-definitions.yaml`](resources/type-definitions.yaml):

```yaml
  containerExamples.Reverse:
    extends: containerExamples.BaseTask
    description: "Reverses the given text"
    input-properties:
      text:
        kind: string
        required: true
    output-properties:
      reversed:
        kind: string
```

**2. Write the class** in `src/reverse.py` — class name **must** be `Reverse` (matches the
type after the dot):

```python
from digitalai.release.integration import BaseTask


class Reverse(BaseTask):
    def execute(self) -> None:
        text = self.input_properties['text']
        if not text:
            raise ValueError("The 'text' field cannot be empty")
        self.set_output_property('reversed', text[::-1])
```

**3. Write a test** in `tests/unit/test_reverse.py` (see [Testing your task](#testing-your-task)).

**4. Build & install** — bump `VERSION` in `project.properties`, then run the build
(see [Build, install, run](#build-install-run)). Add the task to a template and run it.

That's the whole loop: **declare → implement → test → build → run.**

---

## The example tasks explained

The template ships a set of examples, each demonstrating one capability. Use them as
starting points.

| Type (YAML) | Class (`src/`) | Base class | Demonstrates |
|-------------|----------------|------------|--------------|
| `containerExamples.Hello` | `Hello` ([hello.py](src/hello.py)) | `BaseTask` | The minimal task: read an input, set an output, add a comment. |
| `containerExamples.ServerQuery` | `ServerQuery` ([sample_server_task.py](src/sample_server_task.py)) | `BaseTask` | Calling a **third-party** HTTP API using a `ci` server connection for the URL/credentials. |
| `containerExamples.TestConnection` | `TestConnection` ([test_connection.py](src/test_connection.py)) | `BaseTask` | A **test-connection** script for a server CI: returns `{success, output}` in `commandResponse`. |
| `containerExamples.SetSystemMessage` | `SetSystemMessage` ([sample_release_api_task.py](src/sample_release_api_task.py)) | `BaseTask` | Calling the **Release** REST API the manual way via `get_release_api_client()`. |
| `containerExamples.CreateAndStartRelease` | `CreateAndStartRelease` ([create_and_start_release.py](src/create_and_start_release.py)) | `ApiBaseTask` | Orchestrating the Release API with the ready-made `templateApi` / `releaseApi` / `phaseApi` / `taskApi` wrappers. |
| `containerExamples.NameLookup` | `NameLookup` ([name_lookup.py](src/name_lookup.py)) | `BaseTask` | A **lookup** script that returns `{label, value}` options for a dropdown. |
| `containerExamples.HelloWithLookup` | `HelloWithLookup` ([hello_with_lookup.py](src/hello_with_lookup.py)) | `BaseTask` | An input whose value is chosen from a lookup (`input-hint.method-ref`). |

### How the key examples were built

**`Hello` — the baseline.** Reads `input_properties['yourName']`, validates it, builds a
greeting, surfaces it with `add_comment`, and returns it via `set_output_property`. Every
other task follows this same shape.

**`ServerQuery` — third-party API + connection CI.** The `server` input is a `ci` referencing
`containerExamples.Server` (a `BasicAuthHttpConnection`). The task reads `url`/`username`/
`password` from that dict and uses `requests` to call the service. This is the pattern for
integrating any external system: model the connection as a CI, call it with `requests`.

**`TestConnection` — validating a connection.** Registered on the `Server` CI as its
`testConnectionScript`, so the **Test** button in the connection dialog runs it. It returns
a `commandResponse` map with `success` and `output`, the shape Release expects.

**`SetSystemMessage` — Release API, manual client.** A `BaseTask` that calls
`self.get_release_api_client()` and issues a raw `client.put("/api/v1/config/...", json=...)`.
Use this when you want full control of the HTTP call.

**`CreateAndStartRelease` — Release API, the easy way.** An `ApiBaseTask` that chains the
typed wrappers: `templateApi.createTemplate` → `templateApi.create` → `releaseApi.getRelease`
→ `phaseApi.updatePhase` → `taskApi.addTask` → `releaseApi.start`. Prefer this over the
manual client whenever you work with the Release API.

**`NameLookup` + `HelloWithLookup` — dynamic dropdowns.** `NameLookup` returns a list of
`{label, value}` entries as `commandResponse`. `HelloWithLookup` wires its `yourName` input
to that script via `input-hint.method-ref`, so the field becomes a populated dropdown.

---

## Testing your task

Tasks are plain Python classes, so you can unit-test them without a server by setting
`input_properties` and calling `execute_task()` (or `execute()` directly). Mock the API
client / `requests` to keep unit tests offline.

```python
from src.reverse import Reverse


def test_reverse():
    task = Reverse()
    task.input_properties = {'task_id': 'task_1', 'text': 'abc'}
    task.execute_task()
    assert task.get_output_properties()['reversed'] == 'cba'
```

Tests live in [`tests/unit/`](tests/unit/) (fast, mocked) and [`tests/integration/`](tests/integration/)
(against a live server, auto-skipped when none is reachable). Run them with:

```sh
uv run pytest               # everything
uv run pytest tests/unit    # fast unit tests only
```

See the [README — Run the tests](README.md#run-the-tests) for the full workflow, including
the `RELEASE_*` environment variables for integration tests.

---

## Build, install, run

The full build/install/run instructions live in the README:

- [Run Release locally](README.md#run-release-locally)
- [Build & publish](README.md#build--publish)
- [Install the plugin into Release](README.md#install-the-plugin-into-release)

The short version: bump `VERSION` in [`project.properties`](project.properties), run
`./build.sh` (or `build.bat`) to build the zip + image and push the image, then
`./build.sh --upload` to install the zip into Release. Add your task to a template and run it.
